from typing import Optional
import time

from mcp.server.fastmcp import FastMCP
import pyte

from ctf_agent.tools.docker_util import DockerShell

server = FastMCP("ctf-agent-workenv")
_shell: Optional[DockerShell] = None


@server.tool()
def workenv_check_connection():
    """
    start docker shell and check if it's responsive.Ensure this is called before other workenv tools.
    """
    global _shell
    if _shell is None:
        _shell = DockerShell()
        try:
            _shell.start()
        except Exception as e:
            _shell = None
            return f"Failed to start docker shell: {e!s}"
    _shell.send(r"export PS1='(CTF_AGENT)\u:\w\$ '")
    time.sleep(0.5)
    _shell.recv_until("(CTF_AGENT)")
    return "Docker shell started successfully."
    # try:
    #     _shell.send("echo CHECK")
    #     out = _shell.recv_rendered(timeout=5)
    #     if "CHECK" in out:
    #         return "Docker workenv is running" + out
    #     return f"Unexpected output: {out!r}"
    # except Exception as e:
    #     return f"Error communicating with docker shell: {e!s}"


@server.tool()
def workenv_run_command(command: str) -> str:
    """
    run a command in the docker work environment and return its output
    all commands are run in the same shell session
    """
    global _shell
    if _shell is None:
        return (
            "Docker shell is not started. Please call workenv_check_connection first."
        )
    try:
        # Use DockerShell.exec_command which waits for the prompt
        _shell.send(command)
        time.sleep(0.5)
        output = _shell.recv_until("(CTF_AGENT)")
        screen = pyte.Screen(80, 24)
        stream = pyte.Stream(screen)
        stream.feed(output)
        lines = list(screen.display)
        return "\n".join(lines)
    except Exception as e:
        return f"Error running command: {e!s}"


if __name__ == "__main__":
    server.run()
