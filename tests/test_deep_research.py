import asyncio
import os
import logging
from dotenv import load_dotenv

# Add the project root to sys.path to allow importing tinyAgent_deepsearch
# This is often needed when running tests directly without full installation
# For a real test suite, you'd typically install the package in editable mode
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from tinyAgent_deepsearch import deep_research, MissingAPIKeyError
except ImportError:
    print("Failed to import from tinyAgent_deepsearch. "
          "Ensure the package is installed or project root is in PYTHONPATH.")
    sys.exit(1)

# Configure basic logging for the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
log = logging.getLogger(__name__)

async def run_test_research():
    """
    Tests the deep_research functionality.
    """
    # Load environment variables from .env file in the project root
    # Assumes .env file is in the parent directory of 'tests/'
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        log.info(f"Loaded .env file from {dotenv_path}")
    else:
        log.warning(f".env file not found at {dotenv_path}. "
                    "Ensure OPENAI_KEY and FIRECRAWL_KEY are set in your environment.")

    # Check for API keys before proceeding
    openai_key = os.getenv("OPENAI_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_KEY")

    if not openai_key:
        log.error("OPENAI_KEY environment variable not set.")
        print("Error: OPENAI_KEY is not set. Please set it in your .env file or environment.")
        return
    if not firecrawl_key:
        log.error("FIRECRAWL_KEY environment variable not set.")
        print("Error: FIRECRAWL_KEY is not set. Please set it in your .env file or environment.")
        return

    log.info("OPENAI_KEY and FIRECRAWL_KEY are set.")

    # Test parameters
    topic = "What are the latest advancements in quantum computing?"
    # Using minimal breadth and depth for a quick test
    breadth = 1
    depth = 1
    # Using a fast and cheap model for testing, if available, or the default
    llm_model_test = os.getenv("TEST_LLM_MODEL", "gpt-4o-mini")


    log.info(f"Starting test research on: '{topic}' with breadth={breadth}, depth={depth}, model='{llm_model_test}'")

    try:
        results = await deep_research(
            topic=topic,
            breadth=breadth,
            depth=depth,
            llm_model=llm_model_test, # Use the test model
            concurrency=1 # Lower concurrency for a simple test
        )

        log.info("\n=== Test Research Complete ===")
        print("\n=== Test Research Complete ===")

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

        # Basic assertions for the test
        assert isinstance(learnings, list), "Learnings should be a list."
        assert isinstance(visited_urls, list), "Visited URLs should be a list."
        # Depending on the topic, you might expect some results.
        # For a very basic test, we just check structure.
        # Add more specific assertions if the test topic is expected to yield consistent results.
        log.info("Test assertions passed.")
        print("\nTest assertions passed.")

    except MissingAPIKeyError as e:
        log.error(f"MissingAPIKeyError during test: {e}")
        print(f"Error: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred during the test: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Running tinyAgent_deepsearch test script...")
    asyncio.run(run_test_research())
    print("\nTest script finished.")