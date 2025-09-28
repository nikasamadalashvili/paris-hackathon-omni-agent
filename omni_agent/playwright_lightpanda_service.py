from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from pydantic import BaseModel

from omni_agent.core.settings import settings


async def scrape_urls_with_lightpanda(urls: list[str]) -> dict[str, Any]:
    """Scrape multiple URLs using Playwright connected to Lightpanda (async).

    Returns a dict with keys: status, combined_content.
    """

    if not urls:
        return {"status": "error", "combined_content": ""}

    if not settings.lightpanda_token:
        return {
            "status": "error",
            "combined_content": "Missing Lightpanda token. Set it in environment or .env.",
        }

    lightpanda_cdp_ws_uri = (
        f"{settings.lightpanda_ws_base}?token={settings.lightpanda_token}"
    )

    async with async_playwright() as playwright:
        browser: Browser = await playwright.chromium.connect_over_cdp(
            lightpanda_cdp_ws_uri
        )
        try:
            if browser.contexts:
                browser_context: BrowserContext = browser.contexts[0]
            else:
                browser_context = await browser.new_context()

            page_list: list[Page] = []
            for _ in urls:
                page_list.append(await browser_context.new_page())

            navigation_tasks = [
                page_list[i].goto(
                    urls[i],
                    wait_until="load",
                    timeout=int(settings.default_timeout * 1000),
                )
                for i in range(len(urls))
            ]
            await asyncio.gather(*navigation_tasks, return_exceptions=True)

            # Optional: wait for network to settle a bit on each page
            network_idle_tasks = [
                page_list[i].wait_for_load_state("networkidle")
                for i in range(len(urls))
            ]
            await asyncio.gather(*network_idle_tasks, return_exceptions=True)

            combined_sections: list[str] = []
            html_content_tasks = [page_list[i].content() for i in range(len(urls))]
            page_html_results = await asyncio.gather(
                *html_content_tasks, return_exceptions=True
            )

            for i, html_or_error in enumerate(page_html_results):
                url = urls[i]
                if isinstance(html_or_error, Exception):
                    print(f"Error scraping {url}: {html_or_error}")
                    continue
                html = html_or_error or ""
                if html.strip():
                    combined_sections.append(f"# Content from {url}\n\n{html}\n\n---\n")

            if not combined_sections:
                return {
                    "status": "error",
                    "combined_content": "Could not scrape any content from the given URLs",
                }

            return {
                "status": "success",
                "combined_content": "\n".join(combined_sections),
            }
        finally:
            await browser.close()


async def run_example() -> None:
    # Hardcoded example URL(s)
    example_urls = [
        "https://publika.ge/article/ver-dadasturda-jgufuri-dzaladoba-tumca-ras-wers-mchedlishvili-8-piris-ganachenshi/"
    ]
    result = await scrape_urls_with_lightpanda(example_urls)
    print(result.get("combined_content", result.get("combined_content", "")))


def main() -> None:
    asyncio.run(run_example())


# -------- Minimal FastAPI app --------
app = FastAPI()


class ScrapeUrlsRequest(BaseModel):
    urls: list[str]


@app.post("/scrape")
async def post_scrape(req: ScrapeUrlsRequest) -> dict[str, Any]:
    return await scrape_urls_with_lightpanda(req.urls)


if __name__ == "__main__":
    main()
