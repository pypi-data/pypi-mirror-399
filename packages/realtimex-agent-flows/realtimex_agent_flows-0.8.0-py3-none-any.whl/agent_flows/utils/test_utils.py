"""Utility functions for handling test manifests."""

from typing import Any

from agent_flows.models.test import TestManifest


def parse_test_manifest(
    test_manifest: str | dict[str, Any] | TestManifest | None,
) -> TestManifest | None:
    """Parse test manifest from various input types.

    Args:
        test_manifest: Test manifest input (file path, dict, instance, or None)

    Returns:
        Parsed TestManifest instance or None if no manifest provided

    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If manifest data is invalid or type is incorrect
    """
    if test_manifest is None:
        return None

    if isinstance(test_manifest, TestManifest):
        return test_manifest

    if isinstance(test_manifest, dict):
        try:
            return TestManifest.from_dict(test_manifest)
        except Exception as e:
            raise ValueError(f"Invalid test manifest dictionary: {str(e)}") from e

    if isinstance(test_manifest, str):
        try:
            return TestManifest.from_file(test_manifest)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to load test manifest from file: {str(e)}") from e

    raise ValueError(
        f"Invalid test_manifest type: {type(test_manifest)}. "
        "Expected str (file path), dict, TestManifest instance, or None."
    )
