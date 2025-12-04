import os

from pydantic_ai.mcp import MCPServerStdio

from ..util.logger import register_logger

logger = register_logger(__name__)

def _default_third_party():
    return [
        MCPServerStdio("uv",args=["run", ".venv/lib/python3.12/site-packages/ida_pro_mcp/server.py"],timeout=30),
    ]


def setup_toolsets():
    servers = []
    servers.append(MCPServerStdio("uv", args=["run", "src/ctf_agent/tools/docker_mcp.py","--mount", "dataset:/workspace"], timeout=30))
    return _default_third_party() + servers


__all__ = ["setup_toolsets"]