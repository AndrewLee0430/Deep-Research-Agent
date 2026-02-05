"""
Deep Research v2 - Planner Agent
支援動態搜尋數量和兩階段規劃
"""

from pydantic import BaseModel, Field
from agents import Agent
from typing import Optional
from config import ResearchDepth, DEPTH_SEARCH_COUNT, OutputLanguage

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")
    priority: int = Field(default=1, description="Priority level 1-3, where 1 is highest priority")
    category: str = Field(default="general", description="Category: background, data, news, examples, risks")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform.")
    identified_gaps: list[str] = Field(default=[], description="Information gaps that may need follow-up searches")


def get_planner_instructions(num_searches: int, language: OutputLanguage) -> str:
    lang_hint = {
        OutputLanguage.ENGLISH: "Search in English primarily.",
        OutputLanguage.TRADITIONAL_CHINESE: "優先使用繁體中文搜尋，但重要主題也搜尋英文來源。",
        OutputLanguage.SIMPLIFIED_CHINESE: "优先使用简体中文搜索，但重要主题也搜索英文来源。",
        OutputLanguage.JAPANESE: "日本語で検索を優先しますが、重要なトピックは英語ソースも検索してください。",
        OutputLanguage.KOREAN: "한국어 검색을 우선하되 중요한 주제는 영어 소스도 검색하세요.",
    }.get(language, "Search in English primarily.")
    
    return f"""
You are a strategic research planner. Given a query, design an optimal search strategy.

Output exactly {num_searches} search queries.

{lang_hint}

Requirements:
1. Each search must cover a DISTINCT angle:
   - background: Definitions, context, history
   - data: Statistics, market data, reports, studies
   - news: Latest developments, recent news (2024-2025)
   - examples: Case studies, real-world applications
   - risks: Limitations, challenges, criticisms

2. Assign priorities:
   - Priority 1: Essential for answering the core query
   - Priority 2: Important supporting information
   - Priority 3: Nice-to-have context

3. At least {max(1, num_searches // 3)} queries must include recency hints ("2024", "2025", "latest", "recent")

4. Avoid duplicate or near-duplicate queries

5. Identify potential information gaps that might need follow-up research

Be specific. Include key entities, constraints, evaluation terms where relevant.
"""


def create_planner_agent(depth: ResearchDepth, language: OutputLanguage) -> Agent:
    """Create a planner agent with the specified depth"""
    num_searches = DEPTH_SEARCH_COUNT[depth]
    return Agent(
        name="PlannerAgent",
        instructions=get_planner_instructions(num_searches, language),
        model="gpt-4o-mini",
        output_type=WebSearchPlan,
    )


# Follow-up planner for phase 2
class FollowUpSearchPlan(BaseModel):
    needs_followup: bool = Field(description="Whether follow-up searches are needed")
    searches: list[WebSearchItem] = Field(default=[], description="Follow-up searches to fill gaps")
    reasoning: str = Field(description="Explanation of what gaps were identified")


FOLLOWUP_PLANNER_INSTRUCTIONS = """
You are a research gap analyzer. Given the original query and initial search results summaries,
determine if there are critical information gaps that need additional searches.

Analyze:
1. Are there unanswered aspects of the original query?
2. Are there conflicting information that needs verification?
3. Are there missing data points (numbers, dates, sources)?
4. Are there mentioned topics that need deeper exploration?

If gaps exist, propose 2-3 targeted follow-up searches.
If the initial research is comprehensive, set needs_followup to false.

Be conservative - only suggest follow-ups for CRITICAL gaps, not nice-to-haves.
"""

followup_planner_agent = Agent(
    name="FollowUpPlannerAgent",
    instructions=FOLLOWUP_PLANNER_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=FollowUpSearchPlan,
)
