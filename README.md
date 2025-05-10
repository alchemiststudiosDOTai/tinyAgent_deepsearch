# tinyAgent_deepsearch

![tinyAgent_deepsearch Logo](./tinyagent_deepsearch.png)

`tinyAgent_deepsearch` is a Python library from [Alchemist Studios AI](https://github.com/alchemiststudiosDOTai), developed by [tunahorse21 (larock22)](https://x.com/tunahorse21), designed to facilitate deep research on various topics using AI agents, powered by OpenAI and Firecrawl for web scraping and content analysis. It leverages the `tiny_agent_os` framework for structuring AI agent interactions.

> **Note:** Currently, `tinyAgent_deepsearch` uses Firecrawl for web research and content extraction. In the future, the plan is to combine various agents and tools—including `tiny_agent_os`, browser-based agents (such as browser-use), and other agentic utilities—to enable even more powerful, multi-modal research workflows. Stay tuned for updates as the project evolves!

## Features

*   Perform recursive, multi-step research on a given topic.
*   Generate focused search queries based on evolving learnings.
*   Utilize Firecrawl to scrape web content.
*   Employ OpenAI's language models to digest information and identify follow-up questions.
*   Configurable research depth and breadth.

## Installation

You can install `tinyAgent_deepsearch` using pip:

```bash
pip install tinyAgent_deepsearch 
```
*(Note: This command assumes the package will be published to PyPI. For local installation from source, navigate to the project root directory where `pyproject.toml` is located and run `pip install .`)*

## Prerequisites

Before using the library, ensure you have the following API keys set as environment variables:

*   `OPENAI_KEY`: Your API key for OpenAI.
*   `FIRECRAWL_KEY`: Your API key for Firecrawl.

You can set them in your shell environment or by using a `.env` file in your project root (requires `python-dotenv` to be installed in your project).

Example `.env` file:
```
OPENAI_KEY="your_openai_api_key_here"
FIRECRAWL_KEY="your_firecrawl_api_key_here"
```

### `tiny_agent_os` Configuration (`config.yml`)

This library relies on the `tiny_agent_os` framework. `tiny_agent_os` typically requires a `config.yml` file in the root of your project for its own operational settings (like default LLM choices, API endpoints for various services, etc.).

While `tinyAgent_deepsearch` allows you to specify the `llm_model` directly for its core research function, the underlying `tiny_agent_os` may still need a `config.yml` to function correctly for its internal operations or if you use `tiny_agent_os` features directly elsewhere in your project.

For detailed information on how to set up the `config.yml` for `tiny_agent_os`, please refer to its official documentation:
[https://github.com/alchemiststudiosDOTai/tinyAgent](https://github.com/alchemiststudiosDOTai/tinyAgent)

Ensure this file is present and correctly configured in your project's root directory if you encounter issues related to `tiny_agent_os` configuration.

## Usage

Here's a basic example of how to use the `deep_research` function:

```python
import asyncio
from tinyAgent_deepsearch import deep_research
from dotenv import load_dotenv # Optional: if you use a .env file

async def main():
    # Optional: Load environment variables from .env file
    # load_dotenv()

    topic = "The future of renewable energy sources"
    breadth = 3  # Number of search queries per depth level
    depth = 2    # Number of recursive research levels

    try:
        print(f"Starting deep research on: {topic}")
        results = await deep_research(
            topic=topic,
            breadth=breadth,
            depth=depth,
            llm_model="gpt-4o-mini", # Optional: specify LLM model
            concurrency=2           # Optional: specify concurrency
        )
        print("\n=== Research Complete ===")
        print("\nLearnings:")
        for i, learning in enumerate(results.get("learnings", [])):
            print(f"{i+1}. {learning}")

        print("\nVisited URLs:")
        for i, url in enumerate(results.get("visited", [])):
            print(f"{i+1}. {url}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

The `deep_research` function accepts the following parameters:

*   `topic` (str): The initial research topic.
*   `breadth` (int): The number of search queries to generate at each depth level.
*   `depth` (int): The number of recursive research levels.
*   `llm_model` (str, optional): The OpenAI model to use. Defaults to `"gpt-4o-mini"`.
*   `concurrency` (int, optional): The maximum number of concurrent search and digest operations. Defaults to `2`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue. (Further details to be added)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.