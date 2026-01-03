"""LLM provider configuration and credential management."""

import os
from collections.abc import Callable, Mapping
from pathlib import Path

from agent_flows.exceptions import CredentialError
from agent_flows.utils.logging import get_logger
from agent_flows.utils.path_utils import get_shared_env_path

try:
    from dotenv import dotenv_values
except ImportError:  # pragma: no cover
    dotenv_values = None  # type: ignore[assignment]

log = get_logger(__name__)


PROVIDER_CREDENTIAL_MAPPINGS: dict[str, list[tuple[str, str, bool]]] = {
    "openai": [
        ("OPEN_AI_KEY", "OPENAI_API_KEY", True),
    ],
    "anthropic": [
        ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY", True),
    ],
    "azure": [
        ("AZURE_OPENAI_KEY", "AZURE_OPENAI_API_KEY", True),
        ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_ENDPOINT", True),
    ],
    "gemini": [
        ("GEMINI_API_KEY", "GEMINI_API_KEY", True),
    ],
    "realtimexai": [
        ("REALTIMEX_AI_API_KEY", "OPENAI_API_KEY", True),
        ("REALTIMEX_AI_BASE_PATH", "OPENAI_API_BASE", True),
    ],
    "ollama": [
        ("OLLAMA_BASE_PATH", "OPENAI_API_BASE", True),
    ],
    "groq": [
        ("GROQ_API_KEY", "GROQ_API_KEY", True),
    ],
    "cohere": [
        ("COHERE_API_KEY", "COHERE_API_KEY", True),
    ],
    "mistral": [
        ("MISTRAL_API_KEY", "MISTRAL_API_KEY", True),
    ],
    "perplexity": [
        ("PERPLEXITY_API_KEY", "PERPLEXITYAI_API_KEY", True),
    ],
    "openrouter": [
        ("OPENROUTER_API_KEY", "OPENROUTER_API_KEY", True),
    ],
    "togetherai": [
        ("TOGETHER_AI_API_KEY", "TOGETHERAI_API_KEY", True),
    ],
    "fireworksai": [
        ("FIREWORKS_AI_LLM_API_KEY", "FIREWORKS_API_KEY", True),
    ],
    "deepseek": [
        ("DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY", True),
    ],
    "xai": [
        ("XAI_LLM_API_KEY", "XAI_API_KEY", True),
    ],
    "novita": [
        ("NOVITA_LLM_API_KEY", "NOVITA_API_KEY", True),
    ],
    "bedrock": [
        ("AWS_BEDROCK_LLM_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID", True),
        ("AWS_BEDROCK_LLM_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY", True),
        ("AWS_BEDROCK_LLM_REGION", "AWS_REGION_NAME", True),
    ],
    "localai": [
        ("LOCAL_AI_BASE_PATH", "OPENAI_API_BASE", True),
        ("LOCAL_AI_API_KEY", "OPENAI_API_KEY", False),
    ],
    "lmstudio": [
        ("LMSTUDIO_BASE_PATH", "OPENAI_API_BASE", True),
    ],
    "textgenwebui": [
        ("TEXT_GEN_WEB_UI_BASE_PATH", "OPENAI_API_BASE", True),
        ("TEXT_GEN_WEB_UI_API_KEY", "OPENAI_API_KEY", False),
    ],
    "koboldcpp": [
        ("KOBOLD_CPP_BASE_PATH", "OPENAI_API_BASE", True),
    ],
    "litellm": [
        ("LITE_LLM_BASE_PATH", "OPENAI_API_BASE", True),
        ("LITE_LLM_API_KEY", "OPENAI_API_KEY", False),
    ],
    "generic-openai": [
        ("GENERIC_OPEN_AI_BASE_PATH", "OPENAI_API_BASE", True),
        ("GENERIC_OPEN_AI_API_KEY", "OPENAI_API_KEY", True),
    ],
    "nvidia-nim": [
        ("NVIDIA_NIM_LLM_BASE_PATH", "OPENAI_API_BASE", True),
    ],
    "huggingface": [
        ("HUGGING_FACE_LLM_API_KEY", "HUGGINGFACE_API_KEY", True),
        ("HUGGING_FACE_LLM_ENDPOINT", "OPENAI_API_BASE", True),
    ],
    "dpais": [
        ("DPAIS_LLM_BASE_PATH", "OPENAI_API_BASE", True),
    ],
    "apipie": [
        ("APIPIE_LLM_API_KEY", "APIPIE_API_KEY", True),
    ],
    "ppio": [
        ("PPIO_API_KEY", "PPIO_API_KEY", True),
    ],
}


class LLMProviderManager:
    """Manages LLM provider configurations and credential mapping for LiteLLM."""

    def __init__(
        self,
        providers: Mapping[str, Mapping[str, str]] | None = None,
        *,
        shared_env_path: Path | str | None = None,
    ) -> None:
        """Initialize the provider manager with explicit dependencies.

        Args:
            providers: Provider configurations mapping provider names to credential dicts.
                       Example: {"openai": {"OPEN_AI_KEY": "sk-..."}, "anthropic": {...}}
                       If None, all credentials will be loaded from shared env file.
            shared_env_path: Optional path to shared .env file for credential fallback.
                             If None, uses get_shared_env_path() from the desktop app environment.
        """
        self.providers = providers or {}
        if shared_env_path is None:
            self.shared_env_path = Path(get_shared_env_path())
        else:
            self.shared_env_path = Path(shared_env_path)

    @classmethod
    def configure(
        cls,
        provider: str,
        *,
        providers: Mapping[str, Mapping[str, str]] | None = None,
        shared_env_path: Path | str | None = None,
        env_setter: Callable[[str, str], None] | None = None,
    ) -> dict[str, str]:
        """Configure provider using classmethod for utility-style invocation.

        This is the recommended way to configure a provider when working within
        the desktop app ecosystem. It uses the shared env file by default.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            providers: Optional provider credentials. If None, loads from shared env file.
            shared_env_path: Optional path to shared env file. If None, uses ecosystem default.
            env_setter: Optional callable to set env vars (for testing)

        Returns:
            Dictionary of environment variables that were set

        Raises:
            ValueError: If provider is not supported
            CredentialError: If required credentials are missing

        Example:
            >>> # Simple usage within desktop app
            >>> LLMProviderManager.configure("openai")
            {'OPENAI_API_KEY': 'sk-...'}

            >>> # Explicit providers for testing
            >>> LLMProviderManager.configure(
            ...     "openai",
            ...     providers={"openai": {"OPEN_AI_KEY": "test-key"}}
            ... )
        """
        manager = cls(providers=providers, shared_env_path=shared_env_path)
        return manager.configure_provider(provider, env_setter=env_setter)

    def get_provider_env_vars(self, provider: str) -> dict[str, str]:
        """Get environment variables for a provider without setting them.

        This is a pure method that does not modify os.environ or any global state.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            Dictionary of LiteLLM-compatible environment variable mappings.
            Example: {"OPENAI_API_KEY": "sk-..."}

        Raises:
            ValueError: If provider is not supported (unknown provider name)
            CredentialError: If required credentials are missing for the provider
        """
        credentials = self._resolve_credentials(provider)
        return self._map_to_litellm_env_vars(provider, credentials)

    def apply_provider_env_vars(
        self,
        env_vars: dict[str, str],
        *,
        env_setter: Callable[[str, str], None] | None = None,
    ) -> None:
        """Apply environment variables to the process environment.

        This is a command method that mutates os.environ (or injected env_setter).

        Args:
            env_vars: Environment variables to set (from get_provider_env_vars)
            env_setter: Optional callable to set env vars. Defaults to os.environ.__setitem__.
                       Signature: (key: str, value: str) -> None
        """
        setter = env_setter or os.environ.__setitem__
        for key, value in env_vars.items():
            if value:
                setter(key, value)
                log.debug(f"Set environment variable '{key}'")

    def configure_provider(
        self,
        provider: str,
        *,
        env_setter: Callable[[str, str], None] | None = None,
    ) -> dict[str, str]:
        """Get and apply environment variables for a provider.

        Convenience method that combines get_provider_env_vars() and apply_provider_env_vars().

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            env_setter: Optional callable to set env vars (for testing)

        Returns:
            Dictionary of environment variables that were set

        Raises:
            ValueError: If provider is not supported
            CredentialError: If required credentials are missing
        """
        env_vars = self.get_provider_env_vars(provider)
        self.apply_provider_env_vars(env_vars, env_setter=env_setter)
        log.debug(f"Configured LiteLLM for provider: {provider}")
        return env_vars

    def _resolve_credentials(self, provider: str) -> dict[str, str]:
        """Resolve credentials for a provider (config -> shared env file fallback).

        Args:
            provider: Provider name

        Returns:
            Merged credentials dictionary
        """
        if provider in self.providers:
            credentials = dict(self.providers[provider])
            log.debug(f"Using credentials for provider '{provider}' from config.")
            return credentials

        log.debug(f"Provider '{provider}' not in config, checking shared env file.")
        return self._load_from_shared_env_file()

    def _load_from_shared_env_file(self) -> dict[str, str]:
        """Load credentials from shared env file if configured.

        Returns:
            Credentials dict from env file, or empty dict if unavailable
        """
        if not self.shared_env_path:
            log.debug("No shared env path configured")
            return {}

        if not self.shared_env_path.exists():
            log.debug("Shared environment file not found", path=str(self.shared_env_path))
            return {}

        if dotenv_values is None:
            log.debug("python-dotenv not installed; skipping shared env file")
            return {}

        log.debug("Loading credentials from shared file", path=str(self.shared_env_path))
        return dotenv_values(str(self.shared_env_path)) or {}

    def _map_to_litellm_env_vars(
        self,
        provider: str,
        credentials: dict[str, str],
    ) -> dict[str, str]:
        """Map provider credentials to LiteLLM environment variables.

        Args:
            provider: Provider name
            credentials: Source credentials dictionary

        Returns:
            Mapped environment variables for LiteLLM

        Raises:
            ValueError: If provider is not supported
            CredentialError: If required credential is missing
        """
        if provider not in PROVIDER_CREDENTIAL_MAPPINGS:
            raise ValueError(f"Unsupported provider: '{provider}'")

        env_vars: dict[str, str] = {}
        mappings = PROVIDER_CREDENTIAL_MAPPINGS[provider]

        for source_key, target_env_var, required in mappings:
            value = credentials.get(source_key, "")

            if required and not value:
                raise CredentialError(
                    f"Missing required credential '{source_key}' for provider '{provider}'"
                )

            if value:
                env_vars[target_env_var] = value

        return env_vars
