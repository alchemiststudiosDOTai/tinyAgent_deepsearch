import os
import asyncio
import logging
import json
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

async def test_report_saving():
    """Test the report saving functionality of deep_research"""
    logger.info("Testing report saving functionality")
    
    # Define parameters for this test
    topic = "quantum computing basics"
    custom_report_dir = os.path.join(project_root, "test_reports")
    custom_report_name = "quantum_test_report"
    
    # Test JSON report
    logger.info(f"Testing JSON report saving to {custom_report_dir}")
    result_json = await deep_research(
        topic=topic,
        breadth=1,
        depth=1,
        save_report=True,
        report_dir=custom_report_dir,
        report_name=custom_report_name,
        report_format="json"
    )
    
    # Verify JSON report was saved
    json_report_path = result_json.get("report_path")
    logger.info(f"JSON report saved to: {json_report_path}")
    assert os.path.exists(json_report_path), f"JSON report not found at {json_report_path}"
    
    # Verify JSON content can be loaded
    with open(json_report_path, 'r') as f:
        json_data = json.load(f)
    assert "learnings" in json_data, "JSON report missing 'learnings' key"
    assert "visited" in json_data, "JSON report missing 'visited' key"
    
    # Test TXT report with auto-generated name
    logger.info("Testing TXT report saving with auto-generated name")
    result_txt = await deep_research(
        topic=topic,
        breadth=1,
        depth=1,
        save_report=True,
        report_dir=custom_report_dir,
        report_format="txt"
    )
    
    # Verify TXT report was saved
    txt_report_path = result_txt.get("report_path")
    logger.info(f"TXT report saved to: {txt_report_path}")
    assert os.path.exists(txt_report_path), f"TXT report not found at {txt_report_path}"
    
    # Verify TXT content can be read
    with open(txt_report_path, 'r') as f:
        txt_content = f.read()
    assert "FINDINGS:" in txt_content, "TXT report missing 'FINDINGS' section"
    assert "SOURCES:" in txt_content, "TXT report missing 'SOURCES' section"
    
    logger.info("Report saving tests passed successfully!")
    return True

if __name__ == "__main__":
    print("\n=== Testing Deep Research Report Saving ===\n")
    success = asyncio.run(test_report_saving())
    if success:
        print("\n✅ All report saving tests passed!")
    else:
        print("\n❌ Report saving tests failed!")
