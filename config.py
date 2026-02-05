"""
Deep Research v2 - Configuration
集中管理所有設定參數
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ResearchDepth(str, Enum):
    QUICK = "quick"      # 3 searches
    STANDARD = "standard"  # 5 searches
    DEEP = "deep"        # 10 searches

class ReportStyle(str, Enum):
    ACADEMIC = "academic"       # 學術報告風格
    BUSINESS = "business"       # 商業簡報風格
    NEWS = "news"              # 新聞稿風格
    EXECUTIVE = "executive"     # 高管摘要風格

class CitationStyle(str, Enum):
    APA = "apa"    # (Smith, 2024)
    MLA = "mla"    # (Smith 45)
    CHICAGO = "chicago"  # Footnotes
    NONE = "none"  # No formal citations

class OutputLanguage(str, Enum):
    ENGLISH = "en"
    TRADITIONAL_CHINESE = "zh-TW"
    SIMPLIFIED_CHINESE = "zh-CN"
    JAPANESE = "ja"
    KOREAN = "ko"

# Depth to search count mapping
DEPTH_SEARCH_COUNT = {
    ResearchDepth.QUICK: 3,
    ResearchDepth.STANDARD: 5,
    ResearchDepth.DEEP: 10,
}

class ResearchConfig(BaseModel):
    """研究設定"""
    query: str = Field(description="研究主題")
    depth: ResearchDepth = Field(default=ResearchDepth.STANDARD, description="研究深度")
    language: OutputLanguage = Field(default=OutputLanguage.TRADITIONAL_CHINESE, description="報告語言")
    style: ReportStyle = Field(default=ReportStyle.BUSINESS, description="報告風格")
    citation_style: CitationStyle = Field(default=CitationStyle.APA, description="引用格式")
    enable_fact_check: bool = Field(default=True, description="啟用事實查核")
    enable_two_phase_search: bool = Field(default=True, description="啟用兩階段搜尋")
    send_email: bool = Field(default=False, description="完成後寄送郵件")
    email_address: Optional[str] = Field(default=None, description="收件人郵件地址")

# Language display names
LANGUAGE_NAMES = {
    OutputLanguage.ENGLISH: "English",
    OutputLanguage.TRADITIONAL_CHINESE: "繁體中文",
    OutputLanguage.SIMPLIFIED_CHINESE: "简体中文",
    OutputLanguage.JAPANESE: "日本語",
    OutputLanguage.KOREAN: "한국어",
}

# Style display names
STYLE_NAMES = {
    ReportStyle.ACADEMIC: "學術報告",
    ReportStyle.BUSINESS: "商業報告",
    ReportStyle.NEWS: "新聞稿",
    ReportStyle.EXECUTIVE: "高管摘要",
}

# Depth display names
DEPTH_NAMES = {
    ResearchDepth.QUICK: "快速 (3 搜尋)",
    ResearchDepth.STANDARD: "標準 (5 搜尋)",
    ResearchDepth.DEEP: "深入 (10 搜尋)",
}
