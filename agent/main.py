import asyncio
from playwright.async_api import async_playwright

import asyncio
from playwright.async_api import async_playwright
from core.llm import VLMAgent
from core.executor import ActionEngine
from core.graph import create_agent_graph
from dotenv import load_dotenv
import config
import os

# Load environment variables from .env
load_dotenv()

async def main():
    print(f">>> OmniAct Agent Launching (Provider: {config.VLM_PROVIDER})...")
    
    # Use environment variables if set, otherwise fallback to config
    provider = os.getenv("VLM_PROVIDER", config.VLM_PROVIDER)
    objective = os.getenv("AGENT_OBJECTIVE", "Search for 'Rust Programming' on Google")
    
    # Initialize components
    agent_brain = VLMAgent(
        provider=provider, 
        model_name=config.OPENAI_MODEL if provider=="openai" else config.ANTHROPIC_MODEL
    ) 

    async with async_playwright() as p:
        # Launch Browser
        browser = await p.chromium.launch(headless=config.HEADLESS)
        context = await browser.new_context(viewport=config.VIEWPORT)
        page = await context.new_page()
        
        executor = ActionEngine(page)

        print(f"--- Task Started: {objective} ---")
        await page.goto("https://www.google.com")
        await page.wait_for_load_state("networkidle")
        
        # Initialize Graph with Checkpointer
        agent_graph = create_agent_graph(agent_brain, executor, page)
        
        # Initial State
        initial_state = {
            "objective": objective,
            "steps_taken": 0,
            "max_steps": config.MAX_STEPS,
            "history": [],
            "screenshot": None,
            "text_map": None,
            "elements": [],
            "decision": None,
            "last_raw_screenshot": None,
            "status": "running",
            "error_count": 0
        }

        # LangGraph thread config for persistence
        run_config = {"configurable": {"thread_id": "session_001"}}

        # Run Graph
        result = await agent_graph.ainvoke(initial_state, config=run_config)
        
        print(f"\n>>> Task Finished with status: {result['status']}")
        
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
