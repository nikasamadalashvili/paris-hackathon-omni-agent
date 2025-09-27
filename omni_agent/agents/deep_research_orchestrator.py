from __future__ import annotations

from google.adk.agents import SequentialAgent

from omni_agent.agents.analysis.claim_structuring_agent import claim_structuring_agent
from omni_agent.agents.analysis.gap_identification_agent import gap_identification_agent
from omni_agent.agents.research.research_orchestrator_agent import (
    research_orchestrator_agent,
)
from omni_agent.agents.synthesis.evidence_adjudicator_agent import (
    evidence_adjudicator_agent,
)

# Stage 1: Analysis & Strategy (Sequential)
analysis_stage = SequentialAgent(
    name="AnalysisStage",
    sub_agents=[
        claim_structuring_agent,  # structured_claims
        gap_identification_agent,  # structured_claims -> gap_questions
    ],
    description="Analyzes input and creates research strategy",
)

# Stage 2: Parallelized Research (Managed by orchestrator)
research_stage = (
    research_orchestrator_agent  # gap_questions -> comprehensive_answer_set
)

# Stage 3: Synthesis & Verification (Sequential)
synthesis_stage = SequentialAgent(
    name="SynthesisStage",
    sub_agents=[
        evidence_adjudicator_agent,  # adjudicated_report
    ],
    description="Evidence synthesis and report transformation",
)

# Main orchestrator: Analysis -> Research -> Synthesis
deep_research_orchestrator = SequentialAgent(
    name="DeepResearchOrchestrator",
    sub_agents=[analysis_stage, research_stage, synthesis_stage],
    description="Deep Research Orchestrator",
)
