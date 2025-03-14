from xrx_agent_framework.xrx_agent_framework import xrx_reasoning, initialize_async_llm_client
from agent.executor import run_agent

# The rest of the code remains the same
llm_client = initialize_async_llm_client()


app = xrx_reasoning(run_agent=run_agent)()
