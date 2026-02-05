"""
Deep Research v2 - Search Agent
包含來源可信度評分
"""

from pydantic import BaseModel, Field
from agents import Agent, WebSearchTool, ModelSettings
from typing import Optional

class SourceInfo(BaseModel):
    name: str = Field(description="Source name or domain")
    source_type: str = Field(description="Type: official, academic, news, blog, forum, unknown")
    credibility_score: int = Field(description="Credibility 1-5, where 5 is most credible")


class SearchResult(BaseModel):
    summary: str = Field(description="Concise summary of findings (3-6 bullets + 1 paragraph)")
    key_facts: list[str] = Field(description="Key concrete facts (numbers, names, dates)")
    sources: list[SourceInfo] = Field(description="Information about sources found")
    conflicts: Optional[str] = Field(default=None, description="Note any conflicting information found")
    confidence: int = Field(description="Overall confidence in findings 1-5")
    search_query: str = Field(description="The original search query")


SEARCH_INSTRUCTIONS = """
You are a research assistant with expertise in evaluating source credibility.

Given a search term, search the web and produce:
1. A concise summary (3-6 bullets + 1 short paragraph, <300 words)
2. Key concrete facts (numbers, names, dates) - be precise
3. Source evaluation with credibility scores

Credibility scoring guidelines:
- 5: Government sites, peer-reviewed journals, official company sources
- 4: Major news outlets (Reuters, AP, BBC, NYT), established research firms
- 3: Industry publications, reputable blogs, Wikipedia
- 2: Personal blogs, forums, social media
- 1: Unknown sources, obvious bias, outdated information

Source type categories:
- official: Government, company official sites, regulatory bodies
- academic: Journals, university publications, research papers
- news: News organizations, press releases
- blog: Industry blogs, personal blogs, medium posts
- forum: Reddit, Quora, Stack Exchange, discussion boards
- unknown: Cannot determine

If sources disagree, note the conflict clearly.
Capture essence, ignore fluff. No extra commentary beyond the structured output.
"""

search_agent = Agent(
    name="SearchAgent",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
    output_type=SearchResult,
)
