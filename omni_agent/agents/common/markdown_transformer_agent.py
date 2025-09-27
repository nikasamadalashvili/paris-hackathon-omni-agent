from __future__ import annotations

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from omni_agent.core.models import MarkdownOutput
from omni_agent.core.settings import OPENAI_GPT5_NANO_2025_08_07


def create_markdown_transformer_agent(raw_scraped_input: str, output_key: str) -> Agent:
    return Agent(
        model=LiteLlm(model=OPENAI_GPT5_NANO_2025_08_07),
        name="MarkdownTransformerAgent",
        description="Cleans raw text and converts it into research-ready markdown.",
        instruction=f"""
You convert noisy, raw input text into clean, research-ready Markdown.

CLEANING REQUIREMENTS:
- Remove tracking garbage, headers/footers, boilerplate, navigation labels, cookie banners, consent notices.
- Normalize whitespace, fix broken line wraps, collapse repeated blank lines (max one between blocks).
- Decode common encodings (smart quotes, dashes), strip control characters.
- Preserve meaningful content; do not invent facts.

MARKDOWN TRANSFORMATION:
- Use semantic structure: # Title (if clear), ## Headings, ### Subheadings.
- Convert lists and bullets properly; convert tables when structure is clear.
- Inline code for terms or identifiers; fenced code blocks for preformatted text.
- Convert URLs to markdown links: [anchor](url). Keep bare URLs only when no anchor exists.
- Quote clearly marked quotations using > blocks.
- For citations or references, use a References section as a list of links if present.

RESEARCH READINESS:
- Keep chronology and section ordering from the source when it improves comprehension.
- Concise but complete: do not omit substantive data, numbers, or definitions.
- Remove promotional fluff and unrelated calls-to-action.

OUTPUT FORMAT:
Return ONLY the final cleaned Markdown string. No JSON, no commentary.

RAW INPUT:
{raw_scraped_input}
    """,
        output_schema=MarkdownOutput,
        output_key=output_key,
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )
