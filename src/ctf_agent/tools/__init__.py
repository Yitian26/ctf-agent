from pydantic_ai.mcp import MCPServerStdio 

def setup_third_party():
    _ida_pro_mcp = MCPServerStdio('uv',args=["run",".venv/lib/python3.12/site-packages/ida_pro_mcp/server.py"],timeout=10)
    return [_ida_pro_mcp]
    _mcp_run_python = MCPServerStdio('uv', args=['mcp-run-python@latest', 'stdio'], timeout=10)
    return [_mcp_run_python]

def setup_ctf_tools():
    _test_server = MCPServerStdio("uv", args=["run","src/ctf_agent/tools/test_server.py"], timeout=10)
    return [_test_server]

def setup_toolsets():
    return setup_third_party() + setup_ctf_tools()

__all__ = ['setup_toolsets']