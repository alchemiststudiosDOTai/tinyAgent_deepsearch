import asyncio
import os
import logging
from dotenv import load_dotenv

# Attempt to import the installed package
try:
    from tinyAgent_deepsearch import deep_research, MissingAPIKeyError
except ImportError as e:
    print(f"Failed to import from tinyAgent_deepsearch: {e}")
    print("Please ensure the package 'tinyAgent-deepsearch' is installed in your environment.")
    print("You can install it using: pip install tinyAgent-deepsearch")
    exit(1)

# Configure basic logging for this test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
log = logging.getLogger(__name__)

async def main_test():
    """
    Tests the installed deep_research functionality.
    """
    # Load environment variables from .env file in the current directory
    if load_dotenv():
        log.info("Loaded .env file.")
    else:
        log.warning(".env file not found in current directory. "
                    "Ensure OPENAI_KEY and FIRECRAWL_KEY are set in your environment if not using .env.")

    # Check for API keys (optional, as the library itself will raise an error)
    openai_key = os.getenv("OPENAI_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_KEY")

    if not openai_key:
        log.error("OPENAI_KEY environment variable not set from .env or environment.")
    if not firecrawl_key:
        log.error("FIRECRAWL_KEY environment variable not set from .env or environment.")

    # Test parameters
    topic = "Latest breakthroughs in AI-driven drug discovery"
    breadth = 1  # Keep it small for a quick test
    depth = 1    # Keep it shallow for a quick test
    llm_model_to_use = "gpt-4o-mini" # Or any model you prefer for testing

    log.info(f"Starting installed package test research on: '{topic}'")
    print(f"\n--- Starting research on: {topic} ---")

    try:
        results = await deep_research(
            topic=topic,
            breadth=breadth,
            depth=depth,
            llm_model=llm_model_to_use,
            concurrency=1 # Lower concurrency for a simple test
        )

        log.info("--- Test Research Complete ---")
        print("\n--- Test Research Complete ---")

        learnings = results.get("learnings", [])
        visited_urls = results.get("visited", [])

        print("\nLearnings:")
        if learnings:
            for i, learning in enumerate(learnings):
                print(f"{i+1}. {learning}")
        else:
            print("No learnings found.")

        print("\nVisited URLs:")
        if visited_urls:
            for i, url in enumerate(visited_urls):
                print(f"{i+1}. {url}")
        else:
            print("No URLs visited.")

        # Basic assertions
        assert isinstance(learnings, list), "Learnings should be a list."
        assert isinstance(visited_urls, list), "Visited URLs should be a list."
        log.info("Test assertions passed.")
        print("\n--- Test assertions passed ---")

    except MissingAPIKeyError as e:
        log.error(f"MissingAPIKeyError during test: {e}")
        print(f"Error: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred during the test: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("--- Running test script for installed tinyAgent-deepsearch package ---")
    asyncio.run(main_test())
    print("\n--- Test script finished ---")