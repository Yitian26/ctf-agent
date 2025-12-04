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
    names = [
        "test_server",
    ]
    for name in names:
        fname = name if name.endswith(".py") else f"{name}.py"
        abs_path = os.path.join(os.path.dirname(__file__), fname)
        rel_path = os.path.join("src", "ctf_agent", "tools", fname)
        if os.path.exists(abs_path):
            logger.info(f"Found tool : {abs_path}")
            servers.append(MCPServerStdio("uv", args=["run", rel_path], timeout=30))
    return _default_third_party() + servers


__all__ = ["setup_toolsets"]