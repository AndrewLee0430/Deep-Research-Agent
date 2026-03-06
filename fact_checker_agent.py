"""
Deep Research v2 - Fact Checker Agent
驗證搜尋結果的可信度並標註爭議點
"""

from pydantic import BaseModel, Field
from agents import Agent, WebSearchTool, ModelSettings
from typing import Optional

class FactCheckItem(BaseModel):
    claim: str = Field(description="The specific claim being checked")
    verdict: str = Field(description="VERIFIED, PARTIALLY_TRUE, UNVERIFIED, DISPUTED, FALSE")
    confidence: int = Field(description="Confidence in verdict 1-5")
    explanation: str = Field(description="Brief explanation of the verdict")
    supporting_sources: list[str] = Field(default=[], description="Sources that support this claim")
    contradicting_sources: list[str] = Field(default=[], description="Sources that contradict this claim")


class FactCheckReport(BaseModel):
    overall_reliability: int = Field(description="Overall reliability score 1-10")
    checked_facts: list[FactCheckItem] = Field(description="Individual fact checks")
    major_concerns: list[str] = Field(default=[], description="Major reliability concerns found")
    recommendations: list[str] = Field(default=[], description="Recommendations for the report writer")
    summary: str = Field(description="Brief summary of fact-check findings")


FACT_CHECKER_INSTRUCTIONS = """
You are a professional fact-checker. Your job is to verify the accuracy and reliability of research findings.

Given a set of search results and claims, you will:

1. Identify key factual claims (focus on numbers, dates, names, statistics)
2. Cross-reference claims across multiple sources
3. Verify claims through additional targeted searches when needed
4. Rate each claim's reliability

Verdict guidelines:
- VERIFIED: Multiple credible sources agree, high confidence
- PARTIALLY_TRUE: Core claim is accurate but details may vary or be incomplete
- UNVERIFIED: Cannot find sufficient evidence to confirm or deny
- DISPUTED: Sources actively disagree on this point
- FALSE: Clear evidence contradicts the claim

Focus on:
- Statistical claims (market size, growth rates, percentages)
- Attribution claims (who said/did what)
- Timeline claims (when things happened)
- Causal claims (X caused Y)

Be fair but rigorous. Note when claims are opinions vs facts.
Do NOT fact-check subjective statements or predictions.
"""

fact_checker_agent = Agent(
    name="FactCheckerAgent",
    instructions=FACT_CHECKER_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    output_type=FactCheckReport,
)
