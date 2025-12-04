from mcp.server.fastmcp import FastMCP

server = FastMCP("math")

@server.tool()
def add(a: int, b: int) -> int:
    """
    add two integers and return the result
    """
    return a + b

@server.tool()
def get_time() -> str:
    """
    get the current time as a string
    """
    from datetime import datetime
    return datetime.now().isoformat()

server.run()