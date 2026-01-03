"""Credential retrieval and decryption utilities."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
from typing import Any

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from agent_flows.api.http_client import ApiClient
from agent_flows.exceptions import ApiError, CredentialError
from agent_flows.models.config import AgentFlowsConfig
from agent_flows.models.credentials import CredentialBundle, CredentialType
from agent_flows.utils.logging import get_logger
from agent_flows.utils.path_utils import get_shared_env_path

try:  # pragma: no cover - optional dependency is always available in prod envs
    from dotenv import dotenv_values
except ImportError:  # pragma: no cover - fallback when python-dotenv not installed
    dotenv_values = None  # type: ignore[assignment]

log = get_logger(__name__)


class CredentialManager:
    """Loads credential records from the RealTimeX app backend and decrypts them for executors."""

    def __init__(
        self,
        config: AgentFlowsConfig,
        *,
        api_client: ApiClient | None = None,
    ) -> None:
        self._config = config
        self._api_client = api_client or ApiClient(
            base_url=config.app_base_url,
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )
        self._cache: dict[str, CredentialBundle] = {}
        self._cache_lock = asyncio.Lock()

        key, salt = self._load_key_material()
        self._encryption_key = self._derive_key(key, salt)

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        await self._api_client.close()

    async def get(self, credential_id: str, *, force_refresh: bool = False) -> CredentialBundle:
        """Retrieve and decrypt a credential by id."""
        if not force_refresh:
            cached = self._cache.get(credential_id)
            if cached is not None:
                return cached

        async with self._cache_lock:
            if not force_refresh:
                cached = self._cache.get(credential_id)
                if cached is not None:
                    return cached

            raw_record = await self._fetch_credential(credential_id)
            bundle = self._build_bundle(raw_record)
            self._cache[credential_id] = bundle
            return bundle

    def clear_cache(self) -> None:
        """Evict cached credential bundles."""
        self._cache.clear()

    async def _fetch_credential(self, credential_id: str) -> dict[str, Any]:
        try:
            payload = await self._api_client.request("GET", f"/api/v1/credentials/{credential_id}")
        except ApiError as exc:  # pragma: no cover - network errors exercised in integration tests
            raise CredentialError(
                f"Failed to fetch credential '{credential_id}' from credential service",
                credential_id=credential_id,
            ) from exc

        if not isinstance(payload, dict):
            raise CredentialError(
                "Credential service returned an unexpected response",
                credential_id=credential_id,
            )

        return self._extract_credential(payload, credential_id)

    def _extract_credential(self, payload: dict[str, Any], credential_id: str) -> dict[str, Any]:
        status = payload.get("status")
        if status is False:
            raise CredentialError(
                "Credential service reported failure",
                credential_id=credential_id,
                details={"status": status},
            )

        credential = payload.get("credential")
        if not isinstance(credential, dict):
            raise CredentialError(
                "Credential service returned malformed credential payload",
                credential_id=credential_id,
            )

        return credential

    def _build_bundle(self, record: dict[str, Any]) -> CredentialBundle:
        credential_id = str(record.get("id", ""))
        raw_type = record.get("type")
        if not raw_type:
            raise CredentialError("Credential record missing type", credential_id=credential_id)

        try:
            credential_type = CredentialType(raw_type)
        except ValueError as exc:
            raise CredentialError(
                f"Unsupported credential type '{raw_type}'",
                credential_id=credential_id,
            ) from exc

        encrypted_blob = record.get("data")
        if not isinstance(encrypted_blob, str) or not encrypted_blob:
            raise CredentialError("Credential record missing payload", credential_id=credential_id)

        decrypted_json = self._decrypt_blob(encrypted_blob, credential_id)
        payload = self._parse_payload(decrypted_json, credential_type, credential_id)

        metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else None
        updated_at = record.get("updated_at") if isinstance(record.get("updated_at"), str) else None
        name = str(record.get("name")) if record.get("name") is not None else credential_id

        return CredentialBundle(
            credential_id=credential_id,
            name=name,
            credential_type=credential_type,
            payload=payload,
            metadata=metadata,
            updated_at=updated_at,
        )

    def _decrypt_blob(self, encoded_blob: str, credential_id: str) -> str:
        try:
            encrypted_bytes = base64.b64decode(encoded_blob)
        except ValueError as exc:
            raise CredentialError(
                "Credential payload is not valid base64",
                credential_id=credential_id,
            ) from exc

        try:
            encrypted_text = encrypted_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CredentialError(
                "Credential payload is not UTF-8 encoded",
                credential_id=credential_id,
            ) from exc

        try:
            cipher_hex, iv_hex = encrypted_text.split(":", 1)
        except ValueError as exc:
            raise CredentialError(
                "Credential payload is missing initialization vector",
                credential_id=credential_id,
            ) from exc

        try:
            cipher_bytes = bytes.fromhex(cipher_hex)
            iv_bytes = bytes.fromhex(iv_hex)
        except ValueError as exc:
            raise CredentialError(
                "Credential payload contains invalid hex data",
                credential_id=credential_id,
            ) from exc

        cipher = Cipher(algorithms.AES(self._encryption_key), modes.CBC(iv_bytes))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(cipher_bytes) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        try:
            plaintext_bytes = unpadder.update(padded_plaintext) + unpadder.finalize()
        except ValueError as exc:
            raise CredentialError(
                "Credential payload failed padding validation",
                credential_id=credential_id,
            ) from exc

        try:
            return plaintext_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CredentialError(
                "Credential payload could not be decoded",
                credential_id=credential_id,
            ) from exc

    def _parse_payload(
        self,
        payload_json: str,
        credential_type: CredentialType,
        credential_id: str,
    ) -> dict[str, str]:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise CredentialError(
                "Credential payload is not valid JSON",
                credential_id=credential_id,
            ) from exc

        if not isinstance(payload, dict):
            raise CredentialError(
                "Credential payload must be a JSON object",
                credential_id=credential_id,
            )

        if credential_type is CredentialType.BASIC_AUTH:
            username = payload.get("username")
            password = payload.get("password")
            if not isinstance(username, str) or not isinstance(password, str):
                raise CredentialError(
                    "Basic auth credential payload requires username and password",
                    credential_id=credential_id,
                )
            return {"username": username, "password": password}

        if credential_type in {
            CredentialType.HTTP_HEADER,
            CredentialType.QUERY_AUTH,
            CredentialType.ENV_VAR,
        }:
            name = payload.get("name")
            value = payload.get("value")
            if not isinstance(name, str) or not isinstance(value, str):
                raise CredentialError(
                    "Credential payload requires name and value fields",
                    credential_id=credential_id,
                )
            return {"name": name, "value": value}

        raise CredentialError(
            f"Parsing not implemented for credential type '{credential_type.value}'",
            credential_id=credential_id,
        )

    def _load_key_material(self) -> tuple[str, str]:
        env_path = get_shared_env_path()
        if not os.path.exists(env_path):
            raise CredentialError("Shared credential environment file not found")

        env_values = self._load_env_file(env_path)
        key = env_values.get("SIG_KEY")
        salt = env_values.get("SIG_SALT")

        if not key or not salt:
            raise CredentialError("Missing SIG_KEY or SIG_SALT for credential decryption")

        return key, salt

    def _load_env_file(self, env_path: str) -> dict[str, str]:
        if dotenv_values is None:
            log.warning("python-dotenv not installed; cannot load shared .env file", path=env_path)
            return {}

        try:
            values = dotenv_values(env_path) or {}
        except Exception as exc:  # pragma: no cover - defensive guard
            log.warning("Failed to load shared .env file", path=env_path, error=str(exc))
            return {}

        return {key: value for key, value in values.items() if isinstance(value, str)}

    def _derive_key(self, key: str, salt: str) -> bytes:
        try:
            return hashlib.scrypt(
                key.encode("utf-8"),
                salt=salt.encode("utf-8"),
                n=16384,
                r=8,
                p=1,
                dklen=32,
            )
        except ValueError as exc:
            raise CredentialError("Unable to derive encryption key material") from exc
