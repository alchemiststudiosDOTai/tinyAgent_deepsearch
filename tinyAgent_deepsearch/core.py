import os
import math
import asyncio
import logging
from typing import List, Dict, Type

from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp, ScrapeOptions
from openai import AsyncOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Assuming tiny_agent_os provides 'tinyagent' import path
# If 'tiny_agent_os' is the package and it has a 'tinyagent' module:
from tinyagent.decorators import tool
# The tiny_agent function itself is not directly used by the library's core logic,
# but the @tool decorator is.

from .exceptions import MissingAPIKeyError, ConfigurationError

# Initialize logger for the library
log = logging.getLogger(__name__) # Use __name__ for library logger

# Pydantic models
class SearchQuery(BaseModel):
    query: str = Field(..., description="search")
    research_goal: str = Field(..., description="move the search foreward")

class SearchBatch(BaseModel):
    queries: List[SearchQuery]

class SearchDigest(BaseModel):
    learnings: List[str]
    follow_up_questions: List[str]

# Global clients, initialized upon first use or module load after key checks
_openai_client = None
_firecrawl_client = None

def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_KEY")
        if not api_key:
            raise MissingAPIKeyError("OPENAI_KEY")
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client

def get_firecrawl_client() -> FirecrawlApp:
    global _firecrawl_client
    if _firecrawl_client is None:
        api_key = os.getenv("FIRECRAWL_KEY")
        # Firecrawl key can be optional in its constructor, but we might want to enforce it
        if not api_key:
            raise MissingAPIKeyError("FIRECRAWL_KEY")
        _firecrawl_client = FirecrawlApp(
            api_key=api_key,
            api_url=os.getenv("FIRECRAWL_BASE_URL", None)
        )
    return _firecrawl_client

@tool
@retry(wait=wait_random_exponential(min=2, max=8), stop=stop_after_attempt(4))
async def _llm_complete(system: str, prompt: str, schema: Type[BaseModel], llm_model: str) -> BaseModel:
    """
    Internal helper to hit the LLM using the .responses.parse() method.
    """
    client = get_openai_client()
    try:
        response_obj = await client.responses.parse(
            model=llm_model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            text_format=schema,
        )
        data_obj = response_obj.output_parsed
        return data_obj
    except Exception as e:
        log.error(f"LLM completion failed for model {llm_model}: {e}")
        raise ConfigurationError(f"LLM completion error: {e}")


@tool
async def _generate_search_queries(
    topic: str,
    prev_learnings: List[str],
    llm_model: str,
    n: int = 3
) -> List[SearchQuery]:
    system = "You're a research assistant that generates focused search queries. Consider previous learnings and create distinct queries that will uncover new information."
    prompt = f"""Topic: {topic}

    Previous findings:
    {chr(10).join(prev_learnings) if prev_learnings else 'No previous findings'}

    Generate {n} focused search queries that will help deepen understanding of the topic. Each query should have a clear research goal. Please respond with a JSON object containing a list of queries, where each query is a JSON object with 'query' and 'research_goal' properties."""

    batch = await _llm_complete(
        system=system,
        prompt=prompt,
        schema=SearchBatch,
        llm_model=llm_model
    )
    return batch.queries[:n]


@tool
async def _firecrawl_search(q: str, k: int = 2) -> List[dict]:
    firecrawl_client = get_firecrawl_client()
    opts = ScrapeOptions(formats=["markdown"])
    try:
        res = firecrawl_client.search(q, limit=k, scrape_options=opts)
        # Return both markdown and url for each result
        return [{"markdown": item["markdown"][:25_000], "url": item.get("url")}
                for item in res.data if item.get("markdown") and item.get("url")]
    except Exception as e:
        log.error(f"Firecrawl search failed for query '{q}': {e}")
        # Depending on desired behavior, either raise or return empty
        return []


@tool
async def _digest_search_result(
    q: str,
    snippets: List[str],
    llm_model: str,
    max_learn: int = 2,
    max_follow: int = 2
) -> SearchDigest:
    # Indented block starts here
    joined = "\n".join(f"<content>{s}</content>" for s in snippets)
    prompt = (
        f"Analyze search results for: {q}\n"
        f"Produce {max_learn} key learnings and {max_follow} follow-up questions.\n"
        f"Content:\n{joined}"
    )

    return await _llm_complete(
        system="You're a research analyst. Extract insights and identify knowledge gaps from search results.",
        prompt=prompt,
        schema=SearchDigest,
        llm_model=llm_model
    )


async def deep_research(
    topic: str,
    breadth: int,
    depth: int,
    llm_model: str = "gpt-4o-mini",
    concurrency: int = 2,
    learnings: List[str] | None = None,
    visited: List[str] | None = None
) -> Dict:
    """
    Performs deep research on a given topic.

    Args:
        topic: The initial research topic.
        breadth: The number of search queries to generate at each depth level.
        depth: The number of recursive research levels.
        llm_model: The OpenAI model to use for generation and digestion.
        concurrency: The maximum number of concurrent search and digest operations.
        learnings: Optional list of initial learnings.
        visited: Optional list of initially visited URLs.

    Returns:
        A dictionary containing 'learnings' (a list of strings) and
        'visited' (a list of unique URLs).

    Raises:
        MissingAPIKeyError: If OPENAI_KEY or FIRECRAWL_KEY are not set.
        ConfigurationError: For other LLM or configuration related issues.
    """
    # Ensure clients are attempted to be initialized early to catch API key errors
    get_openai_client()
    get_firecrawl_client()

    current_learnings = learnings or []
    current_visited = visited or []

    if depth == 0:
        return {"learnings": list(set(current_learnings)), "visited": list(set(current_visited))}

    log.info(f"Deep research: Topic='{topic}', Breadth={breadth}, Depth={depth}, LLM='{llm_model}'")

    queries = await _generate_search_queries(topic, current_learnings, llm_model, breadth)
    sem = asyncio.Semaphore(concurrency)

    async def handle_query(q: SearchQuery):
        async with sem:
            try:
                log.info(f"Handling query: '{q.query}' with goal: '{q.research_goal}'")
                results = await _firecrawl_search(q.query, k=2) # k=2 is hardcoded as in original
                if not results:
                    log.warning(f"No results from firecrawl for query: {q.query}")
                    return {"learnings": [], "visited": []}

                snippets = [item["markdown"] for item in results]
                urls = [item["url"] for item in results]
            except Exception as e:
                # Check for specific Firecrawl rate limit error if possible, or log generally
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429:
                    log.warning(f"Firecrawl rate limit hit for query '{q.query}'. Skipping.")
                else:
                    log.error(f"Firecrawl search failed for '{q.query}': {e}")
                return {"learnings": [], "visited": []}

            try:
                digest = await _digest_search_result(q.query, snippets, llm_model, max_learn=2, max_follow=2)
            except Exception as e:
                log.error(f"Digest failed for '{q.query}': {e}")
                return {"learnings": [], "visited": []}

            # Prepare for recursive call
            new_learnings = current_learnings + digest.learnings
            new_visited = current_visited + urls
            next_topic_detail = f"{q.research_goal}\n" + "\n".join(digest.follow_up_questions)

            return await deep_research(
                topic=next_topic_detail,
                breadth=math.ceil(breadth / 2), # Halve breadth for subsequent calls
                depth=depth - 1,
                llm_model=llm_model,
                concurrency=concurrency,
                learnings=new_learnings,
                visited=new_visited
            )

    # Gather results from all query handlers
    all_results = await asyncio.gather(*(handle_query(q) for q in queries), return_exceptions=True)

    # Process results, aggregate learnings and visited URLs
    final_learnings = set(current_learnings)
    final_visited = set(current_visited)

    for res_item in all_results:
        if isinstance(res_item, Exception):
            log.error(f"An error occurred during a sub-task of deep_research: {res_item}")
            # Optionally, decide if one error should halt everything or just be logged
            continue # Skip this result
        if isinstance(res_item, dict) and "learnings" in res_item and "visited" in res_item:
            final_learnings.update(res_item["learnings"])
            final_visited.update(res_item["visited"])
        else:
            log.warning(f"Unexpected result structure in deep_research aggregation: {res_item}")


    return {"learnings": list(final_learnings), "visited": list(final_visited)}