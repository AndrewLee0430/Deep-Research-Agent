"""
Deep Research - For Hugging Face Spaces
Fixed version: SSR disabled, new header design, dropdown effects
"""

import gradio as gr
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import sys
import os

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from config import (
    ResearchConfig, ResearchDepth, ReportStyle, 
    CitationStyle, OutputLanguage
)
from research_manager import ResearchManager, ProgressUpdate
from export_utils import export_to_html, export_to_markdown

load_dotenv(override=True)


# ============ CSS - New Header + Dropdown Effects ============

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
.gradio-container { max-width: 100% !important; padding: 0 !important; margin: 0 !important; background: #f8fafc !important; }
footer { display: none !important; }

/* ===== NEW HEADER DESIGN ===== */
.header-section {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    margin: 1rem 1.5rem 0 1.5rem;
    padding: 2.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
}

.header-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 50%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
    pointer-events: none;
}

.header-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.02em;
    position: relative;
    text-shadow: 0 0 60px rgba(6, 182, 212, 0.4);
    animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
    from { filter: drop-shadow(0 0 20px rgba(6, 182, 212, 0.3)); }
    to { filter: drop-shadow(0 0 30px rgba(6, 182, 212, 0.5)); }
}

.header-subtitle {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 0.75rem;
    font-weight: 400;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.main-content { padding: 1rem 1.5rem 1.5rem 1.5rem; }

/* ===== Left Panel ===== */
.left-panel {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.right-panel { display: flex; flex-direction: column; gap: 0.75rem; }

.input-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #06b6d4;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

/* ===== Textbox ===== */
.input-section textarea {
    border: 2px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    background: #fafafa !important;
}

.input-section textarea:focus {
    border-color: #06b6d4 !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
    outline: none !important;
}

/* ===== Buttons ===== */
.btn-start {
    flex: 1;
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    box-shadow: 0 2px 8px rgba(6, 182, 212, 0.3) !important;
    transition: all 0.2s ease !important;
}

.btn-start:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4) !important;
}

.btn-reset {
    background: white !important;
    color: #64748b !important;
    border: 2px solid #e2e8f0 !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.btn-reset:hover {
    border-color: #06b6d4 !important;
    color: #06b6d4 !important;
    background: rgba(6, 182, 212, 0.05) !important;
}

/* ===== Settings Section ===== */
.settings-section { 
    margin-top: 1.25rem; 
    padding-top: 1.25rem; 
    border-top: 1px solid #e2e8f0; 
}

.settings-title {
    font-size: 0.65rem;
    font-weight: 600;
    color: #06b6d4;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
}

/* ===== DROPDOWN STYLING - Pointer & Hover Effects ===== */

/* Target all dropdown containers */
.gr-dropdown,
.gr-form,
div[data-testid="dropdown"] {
    cursor: pointer !important;
}

/* The actual dropdown wrapper */
.gr-dropdown > div,
.gr-form > div {
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 8px !important;
    background: #fafafa !important;
}

/* Hover effect - cyan highlight */
.gr-dropdown:hover > div,
.gr-form:hover > div {
    border-color: #06b6d4 !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
}

/* Focus state */
.gr-dropdown:focus-within > div {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15) !important;
}

/* Dropdown label - make it clickable looking */
.gr-dropdown label,
.gr-form label {
    cursor: pointer !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    transition: color 0.2s ease !important;
}

/* Label turns cyan on hover */
.gr-dropdown:hover label,
.gr-form:hover label {
    color: #06b6d4 !important;
}

/* The dropdown arrow/chevron */
.gr-dropdown svg,
.gr-form svg {
    color: #94a3b8 !important;
    transition: all 0.2s ease !important;
}

.gr-dropdown:hover svg,
.gr-form:hover svg {
    color: #06b6d4 !important;
    transform: translateY(1px);
}

/* Select element itself */
select, 
.gr-dropdown select,
.gr-dropdown input {
    cursor: pointer !important;
}

/* Checkbox styling */
input[type="checkbox"] {
    cursor: pointer !important;
    accent-color: #06b6d4 !important;
}

/* ===== Progress Card ===== */
.progress-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.progress-title { font-size: 0.85rem; font-weight: 600; color: #1e293b; }
.progress-percent { font-size: 0.85rem; font-weight: 700; color: #06b6d4; }

.progress-bar {
    background: #e2e8f0;
    border-radius: 6px;
    height: 6px;
    overflow: hidden;
    margin-bottom: 0.75rem;
}

.progress-fill {
    background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
    height: 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
}

.progress-status { font-size: 0.85rem; color: #475569; margin-bottom: 0.75rem; }
.step-list { border-top: 1px solid #e2e8f0; padding-top: 0.5rem; }

.step-item { display: flex; align-items: center; padding: 0.3rem 0; font-size: 0.8rem; color: #94a3b8; }
.step-item.done { color: #1e293b; }
.step-item.active { color: #06b6d4; font-weight: 500; }

.step-dot { width: 6px; height: 6px; border-radius: 50%; background: #cbd5e1; margin-right: 0.5rem; }
.step-item.done .step-dot { background: #06b6d4; }
.step-item.active .step-dot { background: #06b6d4; animation: pulse 1.5s infinite; }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.3); }
}

/* ===== Report Card ===== */
.report-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    min-height: 300px;
}

.report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}

.report-title { font-size: 0.85rem; font-weight: 600; color: #1e293b; }

.btn-export {
    background: #f1f5f9 !important;
    border: none !important;
    color: #475569 !important;
    padding: 0.4rem 0.75rem !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    margin-left: 0.4rem !important;
    transition: all 0.2s ease !important;
}

.btn-export:hover { 
    background: #06b6d4 !important; 
    color: white !important; 
}

.report-content { font-size: 0.9rem; line-height: 1.7; color: #334155; }
.report-content h1 { font-size: 1.4rem; margin-bottom: 0.75rem; color: #0f172a; font-weight: 700; }
.report-content h2 { 
    font-size: 1.15rem; 
    margin-top: 1.5rem; 
    margin-bottom: 0.5rem; 
    padding-bottom: 0.4rem; 
    border-bottom: 2px solid #06b6d4; 
    color: #0f172a; 
    font-weight: 600;
}
.report-content h3 { font-size: 1rem; margin-top: 1rem; color: #1e293b; font-weight: 600; }
.report-content p { margin-bottom: 0.75rem; }
.report-content ul, .report-content ol { padding-left: 1.5rem; margin-bottom: 0.75rem; }
.report-content li { margin-bottom: 0.25rem; }
.report-content table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem; }
.report-content th, .report-content td { border: 1px solid #e2e8f0; padding: 0.6rem; text-align: left; }
.report-content th { background: linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(8, 145, 178, 0.08) 100%); font-weight: 600; }
"""


# ============ HTML Helpers ============

def progress_html(query, pct, status, steps):
    steps_html = "".join([
        f'<div class="step-item {"done" if s.get("done") else "active" if s.get("active") else ""}">'
        f'<div class="step-dot"></div>{s["label"]}</div>'
        for s in steps
    ])
    
    return f"""
    <div class="progress-card">
        <div class="progress-header">
            <span class="progress-title">Researching: {query[:50]}{'...' if len(query) > 50 else ''}</span>
            <span class="progress-percent">{int(pct*100)}%</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" style="width:{int(pct*100)}%"></div></div>
        <div class="progress-status">{status}</div>
        <div class="step-list">{steps_html}</div>
    </div>
    """


def empty_progress():
    return """
    <div class="progress-card" style="text-align:center;color:#64748b;padding:2.5rem 1rem;">
        <div style="font-size:2.5rem;margin-bottom:0.75rem;">🔬</div>
        <div style="font-size:0.95rem;">Enter a topic and click <strong style="color:#06b6d4;">Start Research</strong></div>
    </div>
    """


# ============ Research Function ============

async def do_research(query, depth, lang, style, do_email, email_addr):
    if not query or not query.strip():
        yield empty_progress(), "*Enter a research topic to begin*", gr.update(interactive=True), gr.update(visible=False), gr.update(visible=False)
        return
    
    yield progress_html(query, 0.05, "Starting...", []), "*Research in progress...*", gr.update(interactive=False), gr.update(visible=False), gr.update(visible=False)
    
    depth_map = {"Quick": ResearchDepth.QUICK, "Standard": ResearchDepth.STANDARD, "Deep": ResearchDepth.DEEP}
    lang_map = {"English": OutputLanguage.ENGLISH, "繁體中文": OutputLanguage.TRADITIONAL_CHINESE, "简体中文": OutputLanguage.SIMPLIFIED_CHINESE, "日本語": OutputLanguage.JAPANESE, "한국어": OutputLanguage.KOREAN}
    style_map = {"Academic": ReportStyle.ACADEMIC, "Business": ReportStyle.BUSINESS, "News": ReportStyle.NEWS, "Executive": ReportStyle.EXECUTIVE}
    
    config = ResearchConfig(
        query=query,
        depth=depth_map.get(depth, ResearchDepth.STANDARD),
        language=lang_map.get(lang, OutputLanguage.ENGLISH),
        style=style_map.get(style, ReportStyle.BUSINESS),
        citation_style=CitationStyle.APA,
        enable_fact_check=True,
        enable_two_phase_search=True,
        send_email=bool(do_email),
        email_address=email_addr if do_email and email_addr else None,
    )
    
    steps = [
        {"id": "plan", "label": "Planning searches"},
        {"id": "search", "label": "Searching web"},
        {"id": "analyze", "label": "Analyzing & fact-checking"},
        {"id": "write", "label": "Writing report"},
    ]
    
    manager = ResearchManager()
    
    try:
        async for update in manager.run(config):
            if isinstance(update, ProgressUpdate):
                for s in steps:
                    s["done"] = False
                    s["active"] = False
                    
                    if s["id"] == "plan" and update.stage not in ["init", "planning"]:
                        s["done"] = True
                    if s["id"] == "search" and update.stage in ["analyzing_gaps", "fact_checking", "fact_check_complete", "writing", "writing_complete", "complete", "sending_email", "email_sent"]:
                        s["done"] = True
                    if s["id"] == "analyze" and update.stage in ["writing", "writing_complete", "complete", "sending_email", "email_sent"]:
                        s["done"] = True
                    if s["id"] == "write" and update.stage in ["complete", "sending_email", "email_sent"]:
                        s["done"] = True
                    
                    if s["id"] == "plan" and update.stage in ["init", "planning"]:
                        s["active"] = True
                    if s["id"] == "search" and update.stage in ["planning_complete", "searching", "followup_searching", "followup_search"]:
                        s["active"] = True
                    if s["id"] == "analyze" and update.stage in ["analyzing_gaps", "fact_checking"]:
                        s["active"] = True
                    if s["id"] == "write" and update.stage in ["fact_check_complete", "writing"]:
                        s["active"] = True
                
                yield progress_html(query, update.progress, update.message, steps), "*Research in progress...*", gr.update(interactive=False), gr.update(visible=False), gr.update(visible=False)
            
            elif isinstance(update, str):
                for s in steps:
                    s["done"] = True
                    s["active"] = False
                yield progress_html(query, 1.0, "✓ Complete!", steps), update, gr.update(interactive=True), gr.update(visible=True), gr.update(visible=True)
    
    except Exception as e:
        error_msg = str(e)[:200]
        yield f'<div class="progress-card" style="color:#dc2626;padding:1.5rem;text-align:center;">❌ Error: {error_msg}</div>', f"**Error:**\n```\n{error_msg}\n```", gr.update(interactive=True), gr.update(visible=False), gr.update(visible=False)


def reset_all():
    return ("", empty_progress(), "*Enter a research topic to begin*", gr.update(interactive=True), gr.update(visible=False), gr.update(visible=False))


def dl_md(report, query):
    if not report or report.startswith("*"):
        return None
    content = export_to_markdown(report, query[:50] if query else "report")
    path = f"/tmp/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def dl_html(report, query):
    if not report or report.startswith("*"):
        return None
    content = export_to_html(report, query[:50] if query else "report")
    path = f"/tmp/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


# ============ UI ============

with gr.Blocks(title="Deep Research", css=CUSTOM_CSS) as demo:
    
    # New Header Design - Rendered gradient text
    gr.HTML("""
    <div class="header-section">
        <h1 class="header-title">Deep Research</h1>
        <p class="header-subtitle">AI-powered Insight Agent</p>
    </div>
    <div class="main-content">
    """)
    
    with gr.Row():
        with gr.Column(scale=1, min_width=340, elem_classes=["left-panel"]):
            gr.HTML('<div class="input-label">Research Topic</div>')
            
            with gr.Column(elem_classes=["input-section"]):
                query_box = gr.Textbox(
                    placeholder="e.g., AI market trends 2025, Electric vehicle industry analysis...",
                    lines=2,
                    show_label=False,
                )
            
            with gr.Row():
                start_btn = gr.Button("Start Research", variant="primary", elem_classes=["btn-start"])
                reset_btn = gr.Button("Reset", elem_classes=["btn-reset"])
            
            with gr.Column(elem_classes=["settings-section"]):
                gr.HTML('<div class="settings-title">⚙️ Settings</div>')
                
                with gr.Row():
                    depth_dd = gr.Dropdown(
                        choices=["Quick", "Standard", "Deep"], 
                        value="Standard", 
                        label="Depth",
                        interactive=True,
                        elem_classes=["gr-dropdown"]
                    )
                    lang_dd = gr.Dropdown(
                        choices=["English", "繁體中文", "简体中文", "日本語", "한국어"], 
                        value="English", 
                        label="Language",
                        interactive=True,
                        elem_classes=["gr-dropdown"]
                    )
                
                style_dd = gr.Dropdown(
                    choices=["Academic", "Business", "News", "Executive"], 
                    value="Business", 
                    label="Report Style",
                    interactive=True,
                    elem_classes=["gr-dropdown"]
                )
                
                gr.HTML('<div class="settings-title" style="margin-top:1rem;">📧 Email Report</div>')
                with gr.Row():
                    email_cb = gr.Checkbox(value=False, label="Send to email")
                    email_tb = gr.Textbox(placeholder="your@email.com", show_label=False, scale=2)
        
        with gr.Column(scale=3, elem_classes=["right-panel"]):
            progress_out = gr.HTML(value=empty_progress())
            
            with gr.Column(elem_classes=["report-card"]):
                with gr.Row(elem_classes=["report-header"]):
                    gr.HTML('<span class="report-title">📄 Research Report</span>')
                    md_btn = gr.Button("Markdown", elem_classes=["btn-export"], visible=False)
                    html_btn = gr.Button("HTML", elem_classes=["btn-export"], visible=False)
                
                file_md = gr.File(visible=False)
                file_html = gr.File(visible=False)
                
                report_out = gr.Markdown("*Enter a research topic to begin*", elem_classes=["report-content"])
    
    gr.HTML('</div>')
    
    # Events
    start_btn.click(
        fn=do_research, 
        inputs=[query_box, depth_dd, lang_dd, style_dd, email_cb, email_tb], 
        outputs=[progress_out, report_out, start_btn, md_btn, html_btn]
    )
    
    query_box.submit(
        fn=do_research, 
        inputs=[query_box, depth_dd, lang_dd, style_dd, email_cb, email_tb], 
        outputs=[progress_out, report_out, start_btn, md_btn, html_btn]
    )
    
    reset_btn.click(
        fn=reset_all,
        outputs=[query_box, progress_out, report_out, start_btn, md_btn, html_btn]
    )
    
    md_btn.click(fn=dl_md, inputs=[report_out, query_box], outputs=file_md).then(
        fn=lambda: gr.update(visible=True), outputs=file_md
    )
    html_btn.click(fn=dl_html, inputs=[report_out, query_box], outputs=file_html).then(
        fn=lambda: gr.update(visible=True), outputs=file_html
    )


# ============ CRITICAL: Launch with SSR disabled ============
if __name__ == "__main__":
    demo.launch(ssr_mode=False)