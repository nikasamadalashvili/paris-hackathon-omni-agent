# ./adk_agent_samples/mcp_client_agent/agent.py
import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

from omni_agent.core.settings import OPENAI_GPT5_NANO_2025_08_07

PROJECT_ROOT = Path(__file__).resolve().parents[2]

root_agent = LlmAgent(
    model=LiteLlm(model=OPENAI_GPT5_NANO_2025_08_07),
    name="web_reader_mcp_client_agent",
    instruction="Use the attached tool to get answer.",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "omni_agent.adk_mcp_server"],
                    cwd=str(PROJECT_ROOT),
                )
            )
        )
    ],
)
