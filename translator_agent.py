"""
Deep Research v2 - Translator Agent
多語言報告生成
"""

from pydantic import BaseModel, Field
from agents import Agent
from config import OutputLanguage

class TranslatedReport(BaseModel):
    translated_content: str = Field(description="The translated report in markdown format")
    translation_notes: list[str] = Field(default=[], description="Notes about translation choices")
    preserved_terms: list[str] = Field(default=[], description="Technical terms kept in original language")


def get_translator_instructions(target_language: OutputLanguage) -> str:
    language_names = {
        OutputLanguage.ENGLISH: "English",
        OutputLanguage.TRADITIONAL_CHINESE: "Traditional Chinese (繁體中文)",
        OutputLanguage.SIMPLIFIED_CHINESE: "Simplified Chinese (简体中文)",
        OutputLanguage.JAPANESE: "Japanese (日本語)",
        OutputLanguage.KOREAN: "Korean (한국어)",
    }
    
    target = language_names.get(target_language, "English")
    
    return f"""
You are a professional translator specializing in research and technical content.

Target Language: {target}

Translation Guidelines:
1. Maintain the original structure and markdown formatting
2. Preserve technical accuracy - don't simplify technical terms incorrectly
3. Keep proper nouns, brand names, and well-known acronyms in their original form
4. Adapt idioms and expressions naturally for the target language
5. Maintain consistent terminology throughout the document

For {target}:
- Use formal/professional register appropriate for research reports
- Ensure numbers, dates, and units are formatted correctly for the locale
- Keep citations and references in their original language but translate surrounding text

Special handling:
- Keep code snippets unchanged
- Keep URLs unchanged
- Technical terms that are commonly used in English (like "AI", "API") can be kept in English
- Note any terms where you made a deliberate translation choice

Produce a complete, properly formatted translation that reads naturally in {target}.
"""


def create_translator_agent(language: OutputLanguage) -> Agent:
    """Create a translator agent for the target language"""
    return Agent(
        name="TranslatorAgent",
        instructions=get_translator_instructions(language),
        model="gpt-4o-mini",
        output_type=TranslatedReport,
    )
