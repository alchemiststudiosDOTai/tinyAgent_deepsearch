# Plan: Converting the Deep Research Project to a Pip Library

## 1. Introduction

The goal is to refactor the existing deep research codebase, currently in [`src/main.py`](src/main.py), into a Python pip-installable library named `tinyAgent_deepsearch`. This library will allow users to easily integrate the deep research functionality into their own projects.

## 2. Library Name

The library will be named `tinyAgent_deepsearch`.

## 3. Core Functionality

The library will provide a primary function, `deep_research`, which takes a research topic, breadth, and depth as input. It will utilize the `tiny_agent_os` framework, Firecrawl, and an OpenAI LLM to perform recursive web searches and return a dictionary of learnings and visited URLs.

## 4. Proposed Project Structure

```
tinyAgent_deepresearch/
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt  # Or dependencies specified in pyproject.toml
├── src/              # Original source, will be refactored or removed
│   ├── .env
│   ├── config.yml
│   ├── main.py
│   ├── old_main.py
│   └── reports/
└── tinyAgent_deepsearch/  # The new library package
    ├── __init__.py      # Exposes public API
    ├── core.py          # Main logic (deep_research, helpers, Pydantic models)
    └── exceptions.py    # Custom exceptions (e.g., for missing API keys)
```

## 5. Key Refactoring Steps from [`src/main.py`](src/main.py)

1.  **Move Core Logic:** The `deep_research` function, helper functions (`llm_complete`, `generate_search_queries`, `firecrawl_search`, `digest_search_result`), and Pydantic models (`SearchQuery`, `SearchBatch`, `SearchDigest`) will be moved from [`src/main.py`](src/main.py) into `tinyAgent_deepsearch/core.py`.
2.  **Remove Script-Specific Code:** The `if __name__ == "__main__":` block in [`src/main.py`](src/main.py) will be removed from the library code. Example usage will be provided in the `README.md` or a separate `examples/` directory.
3.  **Decouple Report Saving:** The functionality for saving reports to a JSON file, currently within the `if __name__ == "__main__":` block, will be removed from the core `deep_research` function. The library function will return the research data, and the user of the library will be responsible for how they want to store or process this data.
4.  **Client Initialization:** Initialization of `openai_client` and `firecrawl` app will be handled within `core.py`, ensuring they are configured when the library functions are called.

## 6. Configuration Handling

*   **API Keys (OpenAI, Firecrawl):**
    *   The library will expect `OPENAI_KEY` and `FIRECRAWL_KEY` to be set as environment variables.
    *   Inside `tinyAgent_deepsearch/core.py`, the code will use `os.getenv("OPENAI_KEY")` and `os.getenv("FIRECRAWL_KEY")`.
    *   If these environment variables are not found, the library will raise a custom exception (e.g., `MissingAPIKeyError` defined in `tinyAgent_deepsearch/exceptions.py`) with an informative message.
*   **Operational Parameters:**
    *   Parameters like `LLM_MODEL` and `CONCURRENCY` (currently global variables in [`src/main.py`](src/main.py)) will become parameters of the `deep_research` function in `tinyAgent_deepsearch/core.py`.
    *   They will have default values matching the current script:
        *   `llm_model: str = "gpt-4o-mini"`
        *   `concurrency: int = 2`
*   **[`src/config.yml`](src/config.yml) and `tiny_agent_os` Configuration:**
    *   The `tinyAgent_deepsearch` library itself will **not** directly read or manage the [`src/config.yml`](src/config.yml) file. This file is typically for configuring the `tiny_agent_os` framework.
    *   The library will assume that `tiny_agent_os` is already configured appropriately in the environment where the library is being used (e.g., `tiny_agent_os` might look for a `config.yml` in the user's project root or use its own default configuration mechanisms).

## 7. Public API

*   The primary public interface will be the `deep_research` function.
*   It will be importable as: `from tinyAgent_deepsearch import deep_research`
*   This will be achieved by importing `deep_research` from `core.py` into `tinyAgent_deepsearch/__init__.py`.
*   The Pydantic models (`SearchQuery`, `SearchBatch`, `SearchDigest`) will reside in `core.py` and be used internally. They will not be part of the initial public API exposed via `__init__.py` to keep the interface minimal, but could be exposed later if a need arises for users to interact with these types directly.

## 8. Dependencies

The library will require the following dependencies, which will be listed in `pyproject.toml` (and potentially `requirements.txt` for reference):

*   `python-dotenv` (for loading `.env` in examples, not strictly by the library itself)
*   `pydantic`
*   `openai`
*   `tenacity`
*   `firecrawl-py`
*   `tiny_agent_os` (confirmed package name)

## 9. Build and Packaging

*   A `pyproject.toml` file will be created to define build system requirements and package metadata (version, author, description, dependencies, entry points if any).
*   Standard build tools like `setuptools`, `flit`, or `poetry` will be used.
*   A `README.md` file will provide installation instructions, basic usage examples, and information on setting up environment variables.
*   A `LICENSE` file (e.g., MIT License) will be included.

## 10. Testing (Conceptual)

While not part of the initial refactoring, consideration should be given to adding unit and integration tests for the library's functionality. This would involve mocking external API calls.

## 11. Documentation

*   Clear docstrings for the public `deep_research` function and any other exposed components.
*   The `README.md` will serve as the primary user documentation.

This plan outlines the steps to transform the current script into a reusable and distributable Python library.