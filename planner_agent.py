"""
Deep Research v2 - Legal Planner Agent
Supports dynamic search depth, jurisdiction routing, and two-phase planning.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from agents import Agent
from config import ResearchDepth, DEPTH_SEARCH_COUNT, OutputLanguage

# ---------------------------------------------------------------------------
# Phase 1: Jurisdiction & Initial Search Planning
# ---------------------------------------------------------------------------

class LegalSearchItem(BaseModel):
    task_id: int = Field(description="Unique identifier for this task.")
    api_target: Literal["US_COURT", "EU_LEX", "EU_HUDOC", "GENERAL_WEB"] = Field(
        description="Target API for this specific search."
    )
    search_query: str = Field(description="Highly optimized English search term suitable for the target API.")
    rationale: str = Field(description="Reasoning for selecting this specific API and query formulation.")
    priority: int = Field(default=1, description="Priority level 1-3 (1 is critical for compliance).")

class LegalResearchPlan(BaseModel):
    analysis: str = Field(description="Brief analysis of the legal query and jurisdiction logic.")
    jurisdiction_type: Literal["US_ONLY", "EU_ONLY", "CROSS_BORDER", "GLOBAL"] = Field(
        description="The determined jurisdiction scope."
    )
    searches: List[LegalSearchItem] = Field(description="List of targeted legal searches.")
    identified_gaps: List[str] = Field(default=[], description="Potential legal nuances needing follow-up.")

def get_planner_instructions(num_searches: int, language: OutputLanguage) -> str:
    lang_hint = {
        OutputLanguage.ENGLISH: "Ensure the final report output logic targets English.",
        OutputLanguage.TRADITIONAL_CHINESE: "The user expects the final report in Traditional Chinese, but all API queries MUST remain in English.",
        OutputLanguage.SIMPLIFIED_CHINESE: "The user expects the final report in Simplified Chinese, but all API queries MUST remain in English.",
        OutputLanguage.JAPANESE: "The user expects the final report in Japanese, but all API queries MUST remain in English.",
        OutputLanguage.KOREAN: "The user expects the final report in Korean, but all API queries MUST remain in English.",
    }.get(language, "Ensure the final report output logic targets English.")

    return f"""
You are a top-tier Legal Tech Strategist and Research Planner. 
Analyze the user's legal or compliance query, determine the correct jurisdiction, and design an optimal search strategy.

Output exactly {num_searches} distinct search tasks.

{lang_hint}

Available API Targets:
- US_COURT: CourtListener (US Federal/State case law, commercial, tech, patent litigation).
- EU_LEX: EUR-Lex (EU regulations, GDPR, AI Act, CJEU rulings).
- EU_HUDOC: HUDOC (European Court of Human Rights, ESG, labor, severe privacy violations).
- GENERAL_WEB: General web search for recent news or business context not found in case law.

Strategy Requirements:
1. Jurisdiction Routing: 
   - If the query is strictly US-focused, route exclusively to US_COURT.
   - If the query involves cross-border compliance (e.g., global data privacy), split the tasks between US_COURT and EU_LEX/EU_HUDOC.
2. Distinct Angles: Each search must cover a different aspect (e.g., core statute, recent precedent, penalty examples).
3. Keyword Optimization: Translate legal concepts into precise English terms optimized for boolean or API searches.
4. Priority: Assign Priority 1 to foundational laws/precedents, and Priority 2/3 to supporting case studies.
"""

def create_planner_agent(depth: ResearchDepth, language: OutputLanguage) -> Agent:
    """
    Create the main legal planner agent.
    Upgraded to Claude 3.5 Sonnet for superior zero-shot classification and strict JSON schema adherence.
    """
    num_searches = DEPTH_SEARCH_COUNT[depth]
    return Agent(
        name="LegalPlannerAgent",
        instructions=get_planner_instructions(num_searches, language),
        model="gemini-3-flash", 
        output_type=LegalResearchPlan,
    )

# ---------------------------------------------------------------------------
# Phase 2: Follow-Up Gap Analysis
# ---------------------------------------------------------------------------

class FollowUpSearchPlan(BaseModel):
    needs_followup: bool = Field(description="True if critical legal or factual gaps remain.")
    searches: List[LegalSearchItem] = Field(default=[], description="Targeted searches to fill the gaps.")
    reasoning: str = Field(description="Explanation of the identified conflicts or missing data.")

FOLLOWUP_PLANNER_INSTRUCTIONS = """
You are a rigorous Legal Fact Checker and Gap Analyzer. 
Review the original query against the summarized results from the Phase 1 API searches.

Analysis Protocol:
1. Contradictions: Do the US and EU sources provide conflicting compliance requirements that need deeper clarification?
2. Missing Precedents: Did the initial search fail to find recent case law (post-2023) for a critical statute?
3. Factual Holes: Are specific penalty figures, implementation dates, or legal definitions missing?

Decision Rule:
If critical gaps exist that pose a compliance risk, set needs_followup to true and propose 2-3 highly targeted searches using the appropriate API target.
If the evidence is solid and comprehensive, set needs_followup to false. Do not suggest searches for trivial details.
"""

followup_planner_agent = Agent(
    name="LegalFollowUpPlannerAgent",
    instructions=FOLLOWUP_PLANNER_INSTRUCTIONS,
    model="gemini-3-flash", 
    output_type=FollowUpSearchPlan,
)