import os
import asyncio
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Add the project root to sys.path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

# Import the library
from tinyagent_deepsearch import deep_research

async def test_custom_model():
    """Test using a custom model with deep_research"""
    logger.info("Testing custom model support")
    
    # Define parameters for this test
    topic = "neural networks overview"
    custom_model = "o4-mini-2025-04-16"  # Use a specific model for testing
    
    logger.info(f"Using custom model: {custom_model}")
    result = await deep_research(
        topic=topic,
        breadth=1,  # Keep scope small for testing
        depth=1,
        llm_model=custom_model,  # Specify the custom model
        save_report=True,  # Save report to verify success
        report_dir=os.path.join(project_root, "test_reports"),
        report_name=f"neural_networks_{custom_model.replace('-', '_')}",
        report_format="json"
    )
    
    # Verify research was successful
    assert "learnings" in result, "Result missing 'learnings' key"
    assert len(result["learnings"]) > 0, "No learnings found using custom model"
    assert "visited" in result, "Result missing 'visited' key"
    assert len(result["visited"]) > 0, "No URLs visited using custom model"
    
    # Verify report was saved
    report_path = result.get("report_path")
    logger.info(f"Report saved to: {report_path}")
    assert os.path.exists(report_path), f"Report not found at {report_path}"
    
    logger.info("Custom model test passed successfully!")
    return True

if __name__ == "__main__":
    print("\n=== Testing Deep Research with Custom Model ===\n")
    success = asyncio.run(test_custom_model())
    if success:
        print("\n\u2705 Custom model test passed!")
    else:
        print("\n\u274c Custom model test failed!")
