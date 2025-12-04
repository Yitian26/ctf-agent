from pydantic_ai.mcp import MCPServerStdio 
from pydantic_ai import Agent

from ..util.config import get_config
from .agent import create_agent
from .builtins import setup_builtins
from ..tools import setup_toolsets

DEBUG = True

def debug():
    import logfire
    logfire.configure()
    logfire.instrument_mcp()
    logfire.instrument_pydantic_ai()

def setup_agent():
    cfg = get_config() 
    toolsets = setup_toolsets()
    agent = create_agent(cfg, toolsets=toolsets)
    setup_builtins(agent)
    return agent

def main():
    if DEBUG:
        debug()
    agent = setup_agent()
    while True:
        userinput = input("You: ")
        result = agent.run_sync(userinput)
        print(result.output)
        # print(result.all_messages())