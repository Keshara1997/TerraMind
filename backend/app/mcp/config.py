import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MCPConfig:
    api_base_url: str
    access_token: str


def get_mcp_config() -> MCPConfig:
    api_base_url = os.getenv(
        "ALEPH_API_BASE_URL",
        "http://localhost:8000/api/v1",
    ).rstrip("/")

    access_token = os.getenv(
        "ALEPH_MCP_ACCESS_TOKEN",
        "",
    ).strip()

    if not access_token:
        raise RuntimeError(
            "ALEPH_MCP_ACCESS_TOKEN is not configured"
        )

    return MCPConfig(
        api_base_url=api_base_url,
        access_token=access_token,
    )