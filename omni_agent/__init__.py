import asyncio
import sys

# Ensure Playwright can spawn subprocesses on Windows by using the Proactor loop
if sys.platform.startswith("win"):
    try:
        policy = asyncio.get_event_loop_policy()
        # Only switch if we're on the Selector policy, which lacks subprocess support
        if isinstance(
            policy, getattr(asyncio, "WindowsSelectorEventLoopPolicy", object)
        ):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        # Best-effort; if anything goes wrong, don't block package import
        pass
