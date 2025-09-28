# my_adk_mcp_server.py
import asyncio
import json
import logging

import mcp.server.stdio  # For running as a stdio server
from google.adk.agents import InvocationContext
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# ADK Tool Imports
from google.adk.tools import AgentTool, ToolContext

# ADK <-> MCP Conversion Utility
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# MCP Server Imports
from mcp import types as mcp_types  # Use alias to avoid conflict
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from omni_agent.agent import root_agent

logger = logging.getLogger(__name__)


adk_tool_to_expose = AgentTool(agent=root_agent)

# --- MCP Server Setup ---
app = Server("adk-tool-exposing-mcp-server")


@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes."""
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    return [mcp_tool_schema]


@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]:  # MCP uses mcp_types.Content
    """MCP handler to execute a tool call requested by an MCP client."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="omni_agent", user_id="test_user"
    )

    # 2. You need to create the top-level InvocationContext
    # You have to provide all this metadata yourself.
    invocation_context = InvocationContext(
        session_service=session_service,
        session=session,
        invocation_id="omni_agent",
        agent=root_agent,
    )
    # Check if the requested tool name matches our wrapped ADK tool
    if name == adk_tool_to_expose.name:
        try:
            # Execute the ADK tool's run_async method.
            # Note: tool_context is None here because this MCP server is
            # running the ADK tool outside of a full ADK Runner invocation.
            # If the ADK tool requires ToolContext features (like state or auth),
            # this direct invocation might need more sophisticated handling.
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments,
                tool_context=ToolContext(invocation_context=invocation_context),
            )
            logger.info(f"ADK tool response: {adk_tool_response}")

            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            error_text = json.dumps(
                {"error": f"Failed to execute tool '{name}': {str(e)}"}
            )
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps(
            {"error": f"Tool '{name}' not implemented by this server."}
        )
        return [mcp_types.TextContent(type="text", text=error_text)]


# --- MCP Server Runner ---
async def run_mcp_stdio_server():
    """Runs the MCP server, listening for connections over standard input/output."""
    # Use the stdio_server context manager from the mcp.server.stdio library
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,  # Use the server name defined above
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    # Define server capabilities - consult MCP docs for options
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    logger.info("Launching MCP Server to expose ADK tools via stdio...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        logger.info("\nMCP Server (stdio) stopped by user.")
    except Exception as e:
        logger.error(f"MCP Server (stdio) encountered an error: {e}")
    finally:
        logger.info("MCP Server (stdio) process exiting.")
# --- End MCP Server ---
