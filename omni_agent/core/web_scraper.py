from typing import Any

import httpx
from google.adk.tools import ToolContext

from omni_agent.agents.common.markdown_transformer_agent import (
    create_markdown_transformer_agent,
)

from .settings import settings


async def scrape_tool(urls: list[str], tool_context: ToolContext) -> dict[str, Any]:
    """Scrape content by calling the local FastAPI Lightpanda service asynchronously.

    Args:
        urls: List of URLs to scrape

    Returns:
        Dictionary containing combined results from all scraped websites
    """

    if not urls:
        return {
            "status": "error",
            "combined_content": "",
        }

    service_url = "http://localhost:8003/scrape"

    async with httpx.AsyncClient(timeout=settings.default_timeout) as client:
        try:
            response = await client.post(service_url, json={"urls": urls})
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "combined_content": f"Failed calling scraper service: {exc}",
            }

    combined_content = data.get("combined_content", "")
    if not combined_content.strip():
        return {
            "status": "error",
            "combined_content": "Could not scrape any content from the given URLs",
        }

    output_key = tool_context.agent_name + "_markdown"

    markdown_transformer_agent = create_markdown_transformer_agent(
        combined_content, output_key
    )

    async for _ in markdown_transformer_agent.run_async(
        tool_context._invocation_context
    ):
        pass

    return {
        "status": "success",
        "combined_content": tool_context.state[output_key].get("markdown"),
    }
