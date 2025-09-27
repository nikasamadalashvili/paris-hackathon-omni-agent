from __future__ import annotations

from pydantic import BaseModel, Field


# Pydantic schemas for agent outputs
class AtomicClaimOutput(BaseModel):
    """Pydantic schema for structured claim output."""

    id: str = Field(description="Unique identifier for the claim")
    text: str = Field(description="The atomic, verifiable claim text")


class StructuredClaimsOutput(BaseModel):
    """Output schema for claim structuring agent."""

    claims: list[AtomicClaimOutput] = Field(
        description="List of structured atomic claims"
    )


class GapQuestionOutput(BaseModel):
    """Pydantic schema for gap question output."""

    id: str = Field(description="Unique identifier for the gap question")
    question: str = Field(description="The critical question to investigate")
    claim_id: str = Field(description="ID of the claim this question relates to")
    question_type: str = Field(
        description="Type: temporal, quantifiable, ambiguous, or implicit"
    )


class GapQuestionsOutput(BaseModel):
    """Output schema for gap identification agent."""

    gap_questions: list[GapQuestionOutput] = Field(
        description="List of critical gap questions"
    )


class ReferenceOutput(BaseModel):
    """Pydantic schema for evidence reference."""

    is_supportive: bool = Field(
        description="Whether this reference supports or refutes the claim"
    )
    citation: str = Field(
        description="Specific quote or key information from the source"
    )
    url: str = Field(description="URL of the source")


class SectionItemOutput(BaseModel):
    """Item within a results section for a claim and its argumentation."""

    claim_id: str = Field(description="ID of the referenced claim")
    claim_text: str = Field(description="Text of the referenced claim")
    argumentative_explanation: str = Field(
        description=(
            "Concise argument explaining why the claim fits this section, "
            "grounded in the provided evidence."
        )
    )


class FactCheckVerdictOutput(BaseModel):
    """Pydantic schema for fact check verdict."""

    claim_id: str = Field(description="ID of the claim being evaluated")
    claim_text: str = Field(description="The original claim text being evaluated")
    verdict: str = Field(
        description="Verdict: verified, false, partially_true, or insufficient_evidence"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the verdict")
    argumentative_explanation: str = Field(
        description="Detailed argumentative explanation of the verdict with reasoning"
    )
    references: list[ReferenceOutput] = Field(
        description="List of references with supportive/refuting indicators"
    )


class EvidenceAdjudicatorOutput(BaseModel):
    """Compact output schema for the main fact-checker agent."""

    what_was_true: list[SectionItemOutput] = Field(
        description="Claims determined true with justifications"
    )
    what_was_false: list[SectionItemOutput] = Field(
        description="Claims determined false with justifications"
    )
    what_could_not_be_verified: list[SectionItemOutput] = Field(
        description=(
            "Claims that are unverifiable or lack sufficient evidence, with "
            "brief justifications"
        )
    )
    references: list[ReferenceOutput] = Field(
        description=(
            "Global list of all references cited across the report. Do not invent URLs."
        )
    )


class ScrapeInput(BaseModel):
    """Pydantic schema for scrape input."""

    urls: list[str] = Field(description="List of URLs to scrape")


class ScrapeOutput(BaseModel):
    """Pydantic schema for scrape output."""

    combined_content: str = Field(description="Combined content from all scraped URLs")
    status: str = Field(description="Status of the scrape operation")


class MarkdownOutput(BaseModel):
    """Output schema for markdown transformation agent."""

    markdown: str = Field(
        description="Cleaned, research-ready markdown representation of the input"
    )
