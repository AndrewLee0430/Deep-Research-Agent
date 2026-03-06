"""
Deep Research v2 - Writer Agent
Multiple report styles and citation integration
"""

from pydantic import BaseModel, Field
from agents import Agent
from typing import Optional
from config import ReportStyle, CitationStyle, OutputLanguage

class ReportData(BaseModel):
    title: str = Field(description="Report title")
    short_summary: str = Field(description="Executive summary (2-3 sentences)")
    markdown_report: str = Field(description="The full report in markdown format")
    key_findings: list[str] = Field(description="Top 5-7 key findings")
    evidence_map: str = Field(description="Markdown table mapping claims to sources")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")
    confidence_assessment: str = Field(description="Overall confidence in the report findings")
    word_count: int = Field(description="Approximate word count of the report")


def get_writer_instructions(
    style: ReportStyle, 
    citation_style: CitationStyle,
    language: OutputLanguage,
    has_fact_check: bool = False
) -> str:
    
    style_guides = {
        ReportStyle.ACADEMIC: """
Academic Report Style:
- Formal, objective tone
- Extensive use of citations
- Structured sections: Abstract, Introduction, Literature Review, Findings, Discussion, Conclusion
- Hedged language ("suggests", "indicates", "appears to")
- Focus on methodology and evidence
- Minimum 2000 words
""",
        ReportStyle.BUSINESS: """
Business Report Style:
- Professional but accessible tone
- Lead with key insights and recommendations
- Structured sections: Executive Summary, Key Findings, Analysis, Recommendations, Appendix
- Use bullet points for clarity
- Include actionable insights
- Data-driven with clear takeaways
- Target 1500-2000 words
""",
        ReportStyle.NEWS: """
News Article Style:
- Inverted pyramid structure (most important first)
- Engaging lead paragraph
- Short paragraphs (2-3 sentences)
- Quotes and attribution
- Objective, journalistic tone
- Accessible to general audience
- Target 800-1200 words
""",
        ReportStyle.EXECUTIVE: """
Executive Summary Style:
- Ultra-concise, high-level overview
- Lead with bottom line/recommendation
- Bullet points for key facts
- No jargon
- Focus on strategic implications
- Clear next steps
- Target 500-800 words
""",
    }
    
    language_instruction = {
        OutputLanguage.ENGLISH: "Write the report in English.",
        OutputLanguage.TRADITIONAL_CHINESE: "用繁體中文撰寫報告。",
        OutputLanguage.SIMPLIFIED_CHINESE: "用简体中文撰写报告。",
        OutputLanguage.JAPANESE: "レポートは日本語で作成してください。",
        OutputLanguage.KOREAN: "보고서를 한국어로 작성하세요.",
    }
    
    fact_check_section = """
Fact Check Integration:
- Include a "Reliability Assessment" section
- Note any disputed or unverified claims
- Highlight high-confidence findings vs. those needing more verification
""" if has_fact_check else ""
    
    return f"""
You are a senior research writer. Create a comprehensive, well-structured report.

{style_guides.get(style, style_guides[ReportStyle.BUSINESS])}

{language_instruction.get(language, "Write in English.")}

Citation Style: {citation_style.value.upper()}
- Integrate citations naturally in the text
- Include an Evidence Map table: | Claim | Supporting Source | Confidence |

{fact_check_section}

Report Structure:
1. Title - Clear, descriptive
2. Executive Summary - 2-3 sentences capturing the essence
3. Key Findings - 5-7 bullet points
4. Main Body - Organized by themes/topics
5. Evidence Map - Table linking claims to sources
6. Conclusion & Recommendations
7. Follow-up Questions - 4-6 suggested research directions
8. Sources/Bibliography

Quality Requirements:
- Do NOT invent facts or citations
- Only use information from the provided search results
- Clearly note when information is limited or uncertain
- Flag any conflicting information
- Maintain consistent formatting

Generate a complete, publication-ready report.
"""


def create_writer_agent(
    style: ReportStyle,
    citation_style: CitationStyle,
    language: OutputLanguage,
    has_fact_check: bool = False
) -> Agent:
    """Create a writer agent with the specified style"""
    return Agent(
        name="WriterAgent",
        instructions=get_writer_instructions(style, citation_style, language, has_fact_check),
        model="gpt-4o-mini",
        output_type=ReportData,
    )