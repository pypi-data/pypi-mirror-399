"""Configuration utilities."""

from agent_flows.models.config import AgentFlowsConfig


def load_config(require_api_key: bool = True) -> AgentFlowsConfig:
    """Load configuration from environment variables.

    This is a simplified configuration loader that only supports environment variables.
    File-based configuration has been removed for simplicity.

    Args:
        require_api_key: Whether to require AGENT_FLOWS_API_KEY. Set to False
                        when using local flow files that don't need API access.

    Returns:
        AgentFlowsConfig instance

    Raises:
        SystemExit: If required environment variables are missing or invalid
    """
    return AgentFlowsConfig.from_env(require_api_key=require_api_key)
