import os
import asyncio
import logging
from dotenv import load_dotenv

# Setup logging to see the tools being used
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Add the project root to sys.path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()
logger.info("Loaded .env file from %s", os.path.join(project_root, '.env'))

# Check if API keys are available
if os.getenv("OPENAI_KEY") and os.getenv("FIRECRAWL_KEY"):
    logger.info("OPENAI_KEY and FIRECRAWL_KEY are set.")
else:
    logger.error("Missing required API keys. Set OPENAI_KEY and FIRECRAWL_KEY in .env file.")
    sys.exit(1)

# Import the library
from tinyagent_deepsearch import deep_research

async def run_test():
    """Run a test to demonstrate tinyagent integration"""
    logger.info("Starting TinyAgent integration test")
    
    # Define a topic for the test
    topic = "artificial general intelligence current state"
    logger.info(f"\nResearching topic: '{topic}'\n")
    logger.info("This will demonstrate the TinyAgent integration and show each tool being used\n")
    
    # Set a small breadth and depth for the test to run quickly
    breadth = 1  # Just one query at each level
    depth = 1    # Just one level deep
    
    # Run the deep_research function which will use tinyagent
    print("\n" + "=" * 50)
    print(f"STARTING DEEP RESEARCH ON: {topic}")
    print("=" * 50 + "\n")
    
    result = await deep_research(
        topic=topic,
        breadth=breadth,
        depth=depth
    )
    
    print("\n" + "=" * 50)
    print("RESEARCH COMPLETE!")
    print("=" * 50)
    
    # Print the report
    print("\n" + "=" * 50)
    print("RESEARCH FINDINGS:")
    print("=" * 50)
    for i, learning in enumerate(result["learnings"], 1):
        print(f"\n{i}. {learning}")
    
    print("\n" + "=" * 50)
    print(f"SOURCES VISITED: {len(result['visited'])}")
    print("=" * 50)
    for i, url in enumerate(result["visited"], 1):
        print(f"{i}. {url}")

    logger.info("Test completed successfully")
    return result

def verify_test_results(result):
    """Verify that the results contain the expected data"""
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "learnings" in result, "Result should contain 'learnings'"
    assert "visited" in result, "Result should contain 'visited'"
    assert len(result["learnings"]) > 0, "Should have at least one learning"
    assert len(result["visited"]) > 0, "Should have at least one visited URL"
    print("\nAll test assertions passed!")

if __name__ == "__main__":
    print("Running tinyAgent integration test...\n")
    result = asyncio.run(run_test())
    verify_test_results(result)
    print("\nTest completed successfully.")
