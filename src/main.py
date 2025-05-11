# tinyagent_deep_research.py - tools for tinyagent to make a deep research like, flow for query

import os
import math
import asyncio
import logging
from typing import List, Dict
from dotenv import load_dotenv
from tinyagent.decorators import tool
from tinyagent.agent import tiny_agent
from pydantic import BaseModel, Field, ValidationError
from firecrawl import FirecrawlApp
from openai import AsyncOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# env and config
load_dotenv()

LLM_MODEL = "gpt-4o-mini"
CONCURRENCY = 2

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
firecrawl = FirecrawlApp(
    api_key=os.getenv("FIRECRAWL_KEY", ""),
    api_url=os.getenv("FIRECRAWL_BASE_URL", None)
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("tinyagent_deep_research")

# pydantic enforcment


class SearchQuery(BaseModel):
    query: str = Field(..., description="search")
    research_goal: str = Field(..., description="move the search foreward")


class SearchBatch(BaseModel):
    queries: List[SearchQuery]


class SearchDigest(BaseModel):
    learnings: List[str]
    follow_up_questions: List[str]

# tooling for tinyagent


tool_usage_log = []

@tool
@retry(wait=wait_random_exponential(min=2, max=8), stop=stop_after_attempt(4))
async def llm_complete(system: str, prompt: str, schema: type[BaseModel]) -> BaseModel:
    entry = f"llm_complete(schema={schema})"
    print(f"[TOOL] {entry}")
    tool_usage_log.append(entry)
    """
    Hit the LLM using the .responses.parse() method for structured output.
    Returns the Pydantic model *instance*.
    """
    response_obj = await openai_client.responses.parse(
        model=LLM_MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        text_format=schema,
    )
    data_obj = response_obj.output_parsed
    return data_obj


@tool
async def generate_search_queries(topic: str, prev_learnings: List[str], n: int = 3) -> List[SearchQuery]:
    entry = f"generate_search_queries(topic={topic}, n={n})"
    print(f"[TOOL] {entry}")
    tool_usage_log.append(entry)
    system = "You're a research assistant that generates focused search queries. Consider previous learnings and create distinct queries that will uncover new information."
    prompt = f"""Topic: {topic}

    Previous findings:
    {chr(10).join(prev_learnings) if prev_learnings else 'No previous findings'}

    Generate {n} focused search queries that will help deepen understanding of the topic. Each query should have a clear research goal. Please respond with a JSON object containing a list of queries, where each query is a JSON object with 'query' and 'research_goal' properties."""

    batch = await llm_complete(
        system=system,
        prompt=prompt,
        schema=SearchBatch
    )
    return batch.queries[:n]


@tool
async def firecrawl_search(q: str, k: int = 2) -> List[dict]:
    entry = f"firecrawl_search(q={q}, k={k})"
    print(f"[TOOL] {entry}")
    tool_usage_log.append(entry)
    from firecrawl import ScrapeOptions
    opts = ScrapeOptions(formats=["markdown"])
    res = firecrawl.search(q, limit=k, scrape_options=opts)
    # Return both markdown and url for each result
    return [{"markdown": item["markdown"][:25_000], "url": item.get("url")} for item in res.data if item.get("markdown") and item.get("url")]


@tool
async def digest_search_result(q: str, snippets: List[str], max_learn: int = 2, max_follow: int = 2) -> SearchDigest:
    entry = f"digest_search_result(q={q}, snippets=[{len(snippets)} items], max_learn={max_learn}, max_follow={max_follow})"
    print(f"[TOOL] {entry}")
    tool_usage_log.append(entry)
    joined = "\n".join(f"<content>{s}</content>" for s in snippets)
    prompt = (
        f"Analyze search results for: {q}\n"
        f"Produce {max_learn} key learnings and {max_follow} follow-up questions.\n"
        f"Content:\n{joined}"
    )

    return await llm_complete(
        system="You're a research analyst. Extract insights and identify knowledge gaps from search results.",
        prompt=prompt,
        schema=SearchDigest
    )


async def deep_research(topic: str, breadth: int, depth: int, learnings: List[str] | None = None,
                        visited: List[str] | None = None) -> Dict:
    learnings = learnings or []
    visited = visited or []

    if depth == 0:
        return {"learnings": learnings, "visited": visited}

    queries = await generate_search_queries(topic, learnings, breadth)
    sem = asyncio.Semaphore(CONCURRENCY)

    async def handle(q: SearchQuery):
        async with sem:
            try:
                results = await firecrawl_search(q.query, k=2)
                snippets = [item["markdown"] for item in results]
                urls = [item["url"] for item in results]
            except Exception as e:
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429:
                    log.warning(f"[Warning] Firecrawl rate limit hit for query '{q.query}'. Skipping.")
                    return {"learnings": [], "visited": []}
                log.error(f"[Error] Firecrawl failed for '{q.query}': {e}")
                return {"learnings": [], "visited": []}
            try:
                digest = await digest_search_result(q.query, snippets, max_learn=2, max_follow=2)
            except Exception as e:
                log.error(f"[Error] Digest failed for '{q.query}': {e}")
                return {"learnings": [], "visited": []}
            next_top = f"{q.research_goal}\n" + "\n".join(digest.follow_up_questions)
            return await deep_research(next_top,
                breadth=math.ceil(breadth/2),
                depth=depth-1,
                learnings=learnings + digest.learnings,
                visited=visited + urls)

    results = await asyncio.gather(*(handle(q) for q in queries))
    flat_learn = {l for r in results for l in r["learnings"]}
    flat_urls = {u for r in results for u in r["visited"]}
    return {"learnings": list(flat_learn), "visited": list(flat_urls)}

if __name__ == "__main__":
    tiny_agent(tools=[generate_search_queries,
               firecrawl_search, digest_search_result])
    topic = "make a report on the state of ai agents"
    result = asyncio.run(deep_research(topic, breadth=3, depth=2))
    print(result)

    # Save the report in src/reports, label by topic
    import json
    import re
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    # Safe filename from topic
    safe_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', topic.lower())[:50]
    report_path = os.path.join(reports_dir, f"{safe_topic}.json")
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Report saved to {report_path}")

# Print the tool usage summary
print("\n=== TOOL USAGE SUMMARY ===")
for i, entry in enumerate(tool_usage_log, 1):
    print(f"{i}. {entry}")
