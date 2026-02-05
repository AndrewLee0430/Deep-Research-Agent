"""
Deep Research - AI-powered Research Agent
Local/Colab version (no HF Spaces dependencies)
"""

import gradio as gr
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import sys
import os

# Windows compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from config import (
    ResearchConfig, ResearchDepth, ReportStyle, 
    CitationStyle, OutputLanguage
)
from research_manager import ResearchManager, ProgressUpdate
from export_utils import export_to_html, export_to_markdown

load_dotenv(override=True)


# ============ CSS ============

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
.gradio-container { max-width: 100% !important; background: #f8fafc !important; }
footer { display: none !important; }

/* Header */
.header-section {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1rem;
}

.header-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.header-subtitle {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Panels */
.left-panel {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* Buttons */
.btn-start {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 1rem !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}

.btn-reset {
    background: white !important;
    color: #64748b !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 10px !important;
}

/* Progress */
.progress-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.progress-bar {
    background: #e2e8f0;
    border-radius: 6px;
    height: 6px;
    overflow: hidden;
    margin: 0.75rem 0;
}

.progress-fill {
    background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
    height: 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
}

/* Report */
.report-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    min-height: 300px;
}

.report-content h2 { 
    border-bottom: 2px solid #06b6d4; 
    padding-bottom: 0.4rem;
    margin-top: 1.5rem;
}
"""


# ============ HTML Helpers ============

def progress_html(query, pct, status):
    return f"""
    <div class="progress-card">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span><strong>Researching:</strong> {query[:50]}{'...' if len(query) > 50 else ''}</span>
            <span style="color:#06b6d4;font-weight:700;">{int(pct*100)}%</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" style="width:{int(pct*100)}%"></div></div>
        <div style="color:#475569;">{status}</div>
    </div>
    """

def empty_progress():
    return """
    <div class="progress-card" style="text-align:center;color:#64748b;padding:2.5rem 1rem;">
        <div style="font-size:2.5rem;margin-bottom:0.75rem;">🔬</div>
        <div>Enter a topic and click <strong style="color:#06b6d4;">Start Research</strong></div>
    </div>
    """


# ============ Research Function ============

async def do_research(query, depth, lang, style):
    if not query or not query.strip():
        yield empty_progress(), "*Enter a research topic to begin*"
        return
    
    yield progress_html(query, 0.05, "Starting..."), "*Research in progress...*"
    
    depth_map = {"Quick (3 searches)": ResearchDepth.QUICK, "Standard (5 searches)": ResearchDepth.STANDARD, "Deep (10 searches)": ResearchDepth.DEEP}
    lang_map = {"English": OutputLanguage.ENGLISH, "繁體中文": OutputLanguage.TRADITIONAL_CHINESE, "简体中文": OutputLanguage.SIMPLIFIED_CHINESE, "日本語": OutputLanguage.JAPANESE, "한국어": OutputLanguage.KOREAN}
    style_map = {"Academic": ReportStyle.ACADEMIC, "Business": ReportStyle.BUSINESS, "News Article": ReportStyle.NEWS, "Executive Summary": ReportStyle.EXECUTIVE}
    
    config = ResearchConfig(
        query=query,
        depth=depth_map.get(depth, ResearchDepth.STANDARD),
        language=lang_map.get(lang, OutputLanguage.ENGLISH),
        style=style_map.get(style, ReportStyle.BUSINESS),
        citation_style=CitationStyle.APA,
        enable_fact_check=True,
        enable_two_phase_search=True,
        send_email=False,
    )
    
    manager = ResearchManager()
    
    try:
        async for update in manager.run(config):
            if isinstance(update, ProgressUpdate):
                yield progress_html(query, update.progress, update.message), "*Research in progress...*"
            elif isinstance(update, str):
                yield progress_html(query, 1.0, "✓ Complete!"), update
    
    except Exception as e:
        error_msg = str(e)[:300]
        yield f'<div class="progress-card" style="color:#dc2626;padding:1.5rem;">❌ Error: {error_msg}</div>', f"**Error:**\n```\n{error_msg}\n```"


def reset_all():
    return "", empty_progress(), "*Enter a research topic to begin*"


# ============ UI ============

with gr.Blocks(title="Deep Research", css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
    
    gr.HTML("""
    <div class="header-section">
        <h1 class="header-title">Deep Research</h1>
        <p class="header-subtitle">AI-powered Insight Agent</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1, min_width=320, elem_classes=["left-panel"]):
            query_box = gr.Textbox(
                label="🔍 Research Topic",
                placeholder="e.g., AI market trends 2025, Electric vehicle industry analysis...",
                lines=3,
            )
            
            with gr.Row():
                start_btn = gr.Button("🚀 Start Research", variant="primary", elem_classes=["btn-start"])
                reset_btn = gr.Button("Reset", elem_classes=["btn-reset"])
            
            gr.Markdown("### ⚙️ Settings")
            
            depth_dd = gr.Dropdown(
                choices=["Quick (3 searches)", "Standard (5 searches)", "Deep (10 searches)"], 
                value="Standard (5 searches)", 
                label="Research Depth",
            )
            lang_dd = gr.Dropdown(
                choices=["English", "繁體中文", "简体中文", "日本語", "한국어"], 
                value="English", 
                label="Output Language",
            )
            style_dd = gr.Dropdown(
                choices=["Academic", "Business", "News Article", "Executive Summary"], 
                value="Business", 
                label="Report Style",
            )
        
        with gr.Column(scale=2):
            progress_out = gr.HTML(value=empty_progress())
            
            gr.Markdown("### 📄 Research Report")
            report_out = gr.Markdown("*Enter a research topic to begin*", elem_classes=["report-content"])
    
    # Events
    start_btn.click(
        fn=do_research, 
        inputs=[query_box, depth_dd, lang_dd, style_dd], 
        outputs=[progress_out, report_out]
    )
    
    query_box.submit(
        fn=do_research, 
        inputs=[query_box, depth_dd, lang_dd, style_dd], 
        outputs=[progress_out, report_out]
    )
    
    reset_btn.click(
        fn=reset_all,
        outputs=[query_box, progress_out, report_out]
    )


# ============ Launch ============
if __name__ == "__main__":
    # For Colab, use share=True to get a public URL
    # For local, share=False is fine
    demo.launch(share=True)
