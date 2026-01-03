"""Path-related utility functions."""

import os


def get_realtimex_user_dir() -> str:
    """Returns the path to the .realtimex.ai user directory."""
    return os.path.join(os.path.expanduser("~"), ".realtimex.ai")


def get_shared_env_path() -> str:
    """Returns the fixed path to the shared environment file."""
    user_dir = get_realtimex_user_dir()
    return os.path.join(user_dir, "Resources", "server", ".env.development")


def get_uvx_executable() -> str:
    """
    Determines the path to the 'uvx' executable.

    Returns:
        The path to the executable, or 'uvx' if not found in standard locations.
    """
    user_dir = get_realtimex_user_dir()
    unix_realtimex_uvx_path = os.path.join(user_dir, "Resources", "envs", "bin", "uvx")
    if os.path.exists(unix_realtimex_uvx_path):
        return unix_realtimex_uvx_path
    win_realtimex_uvx_path = os.path.join(user_dir, "Resources", "envs", "Scripts", "uvx.exe")
    if os.path.exists(win_realtimex_uvx_path):
        return win_realtimex_uvx_path
    return "uvx"


def resolve_bundled_executable(command: str) -> str:
    """
    Resolves bundled executable path for uvx or npx commands.

    Args:
        command: The command to resolve (e.g., 'uvx', 'npx')

    Returns:
        The resolved executable path, or the original command if not found
    """
    if not command or not isinstance(command, str):
        return command

    command_lower = command.strip().lower()
    user_dir = get_realtimex_user_dir()

    if command_lower.startswith("uvx"):
        env_override = os.environ.get("REALTIMEX_UVX_PATH")
        if env_override and os.path.exists(env_override):
            return env_override

        candidates = [
            os.path.join(user_dir, "Resources", "envs", "bin", "uvx"),
            os.path.join(user_dir, "Resources", "envs", "Scripts", "uvx.exe"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

    elif command_lower.startswith("npx"):
        env_override = os.environ.get("REALTIMEX_NPX_PATH")
        if env_override and os.path.exists(env_override):
            return env_override

        node_version = os.environ.get("REALTIMEX_NPX_NODE_VERSION", "v22.16.0")
        candidates = [
            os.path.join(user_dir, ".nvm", "versions", "node", node_version, "bin", "npx"),
            os.path.join("C:", "nvm", node_version, "npx.cmd"),
            os.path.join(user_dir, "Resources", "envs", "Scripts", "npx.cmd"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

    return command
