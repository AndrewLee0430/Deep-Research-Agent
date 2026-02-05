"""
Deep Research v2 - Citation Agent
自動整理引用格式（APA、MLA、Chicago）
"""

from pydantic import BaseModel, Field
from agents import Agent
from typing import Optional
from config import CitationStyle

class Citation(BaseModel):
    id: str = Field(description="Citation ID for in-text reference (e.g., 'smith2024')")
    in_text: str = Field(description="In-text citation format")
    full_reference: str = Field(description="Full reference for bibliography")
    source_url: Optional[str] = Field(default=None, description="URL if available")
    accessed_date: str = Field(description="Date accessed in YYYY-MM-DD format")


class CitationReport(BaseModel):
    citations: list[Citation] = Field(description="All citations in proper format")
    bibliography: str = Field(description="Formatted bibliography section")
    in_text_guide: str = Field(description="Guide for using in-text citations")


def get_citation_instructions(style: CitationStyle) -> str:
    style_guides = {
        CitationStyle.APA: """
APA 7th Edition Format:
- In-text: (Author, Year) or Author (Year)
- Reference: Author, A. A. (Year). Title of work. Publisher. URL

Examples:
- In-text: (Smith, 2024) or Smith (2024) found that...
- Reference: Smith, J. (2024). Research findings on AI. Tech Publisher. https://example.com

For websites:
- Author/Organization. (Year, Month Day). Title. Site Name. URL
- If no author: Title. (Year). Site Name. URL
""",
        CitationStyle.MLA: """
MLA 9th Edition Format:
- In-text: (Author Page) or Author states "quote" (Page)
- Works Cited: Author. "Title." Container, Publisher, Date, URL.

Examples:
- In-text: (Smith 45) or Smith argues that "..." (45)
- Works Cited: Smith, John. "Research on AI." Tech Journal, vol. 5, 2024, pp. 40-50.

For websites:
- Author. "Title." Website Name, Publisher, Day Month Year, URL.
""",
        CitationStyle.CHICAGO: """
Chicago 17th Edition (Notes-Bibliography):
- Footnote: Author, Title (Place: Publisher, Year), page.
- Bibliography: Author. Title. Place: Publisher, Year.

Examples:
- Footnote: ¹ John Smith, Research on AI (New York: Tech Press, 2024), 45.
- Bibliography: Smith, John. Research on AI. New York: Tech Press, 2024.

For websites:
- Footnote: ¹ John Smith, "Title," Website Name, accessed Month Day, Year, URL.
""",
        CitationStyle.NONE: """
No formal citation style required. Simply note sources inline or in a "Sources" section.
Format: Source Name (URL) or "According to [Source]..."
""",
    }
    
    return f"""
You are a citation specialist. Your job is to format citations according to academic standards.

Citation Style: {style.value.upper()}

{style_guides.get(style, style_guides[CitationStyle.APA])}

Given source information from search results, create properly formatted citations.

Rules:
1. Be consistent in formatting
2. Include all available information
3. Use "n.d." for no date
4. Use organization name if no author
5. Always include access date for online sources
6. Generate unique, memorable citation IDs (e.g., 'smith2024', 'techreport2024')

Output a complete bibliography section that can be appended to the report.
"""


def create_citation_agent(style: CitationStyle) -> Agent:
    """Create a citation agent for the specified style"""
    return Agent(
        name="CitationAgent",
        instructions=get_citation_instructions(style),
        model="gpt-4o-mini",
        output_type=CitationReport,
    )
