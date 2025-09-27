# import logging
# from typing import AsyncGenerator

# from google.adk.agents import BaseAgent, InvocationContext
# from google.adk.events import Event

# logger = logging.getLogger(__name__)


# class ScrapeAgent(BaseAgent):
#     """Run SingleQuestionResearchAgent in parallel for each gap question."""

#     def __init__(self) -> None:
#         super().__init__(name="ScrapeAgent")
#         logger.debug(f"Initialized {self.name}")

#     async def _run_async_impl(
#         self, ctx: InvocationContext
#     ) -> AsyncGenerator[Event, None]:
#         gap_questions_output_dict = ctx.session.state.get("gap_questions") or None
#         questions = []

#         logger.debug(
#             f"[{ctx.invocation_id}] {self.name}: Raw gap_questions output: {gap_questions_output_dict}"
#         )

#         ctx.

#         if gap_questions_output_dict is not None:
#             gap_questions_output = GapQuestionsOutput(**gap_questions_output_dict)
#             questions = [item.question for item in gap_questions_output.gap_questions]

#         if not questions:
#             logger.error(
#                 f"[{ctx.invocation_id}] {self.name}: No gap questions found in session state"
#             )
#             return

#         # Step 2: Create batched parallel workflow
#         batch_size = 5
#         batch_parallel_agents = self._create_batch_parallel_agents(
#             questions, batch_size
#         )

#         if not batch_parallel_agents:
#             logger.warning(
#                 f"[{ctx.invocation_id}] {self.name}: No batch agents created"
#             )
#             return

#         # Step 3: Create sequential workflow to orchestrate batches
#         sequential_workflow = SequentialAgent(
#             name="BatchSequentialResearchAgent",
#             sub_agents=batch_parallel_agents,
#         )

#         self.sub_agents.append(sequential_workflow)

#         # Step 4: Execute the sequential workflow and yield its events
#         async for event in sequential_workflow.run_async(ctx):
#             yield event

#         research_answers: list[dict] = []
#         for i, question in enumerate(questions):
#             output_key = f"research_answer_{i}"
#             research_answer = ctx.session.state.get(output_key)
#             if research_answer is None:
#                 logger.warning(
#                     f"[{ctx.invocation_id}] {self.name}: No answer found for key '{output_key}' (question {i})"
#                 )
#                 continue
#             research_answers.append(research_answer)

#         logger.info(
#             f"[{ctx.invocation_id}] {self.name}: Retrieved {len(research_answers)} research answers"
#         )

#         ctx.session.state["research_answers"] = research_answers

#         state_update_event = Event(
#             invocation_id=ctx.invocation_id,
#             author=self.name,
#             actions=EventActions(state_delta={"research_answers": research_answers}),
#         )
#         yield state_update_event


# research_orchestrator_agent = ResearchOrchestratorAgent()
