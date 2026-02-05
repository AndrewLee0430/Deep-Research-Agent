# 🔬 Deep Research

<div align="center">

**AI-powered Insight Agent** - Delivers comprehensive research reports in minutes.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app)
[![OpenAI](https://img.shields.io/badge/OpenAI-Agents%20SDK-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#features) • [Quick Start](#quick-start) • [Usage](#usage) • [Architecture](#architecture)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Smart Search Planning** | AI automatically plans optimal search strategies |
| 🔄 **Two-Phase Search** | Analyzes initial results and fills information gaps |
| ✅ **Fact Checking** | Verifies source credibility with confidence scores |
| 📊 **Multiple Report Styles** | Academic, Business, News, Executive Summary |
| 🌍 **Multi-language** | English, 繁體中文, 简体中文, 日本語, 한국어 |
| 📤 **Export Options** | Markdown, HTML formats |

---

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/deep-research.git
cd deep-research

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the app
python app.py
```

### Option 2: Run on Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/deep-research/blob/main/Deep_Research_Colab.ipynb)

1. Click the badge above
2. Add your OpenAI API key when prompted
3. Run all cells
4. Click the generated link to access the UI

---

## 📖 Usage

### Research Depth Options

| Depth | Searches | Best For |
|-------|----------|----------|
| Quick | 3 | Fast overview, simple topics |
| Standard | 5 | Balanced depth and speed |
| Deep | 10 | Comprehensive research, complex topics |

### Report Styles

- **Academic** - Formal tone, extensive citations, structured sections
- **Business** - Professional, actionable insights, data-driven
- **News Article** - Journalistic style, engaging lead, accessible
- **Executive Summary** - Ultra-concise, strategic implications

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Planner Agent                              │
│         (Designs search strategy, assigns priorities)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Search Agent                               │
│      (Web search + source credibility evaluation)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Follow-up Planner (Optional)                   │
│            (Identifies gaps, plans additional searches)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Fact Checker Agent                           │
│        (Cross-references claims, rates reliability)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Writer Agent                               │
│     (Generates report in specified style and language)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Final Report                               │
│        (Markdown with citations, evidence map, etc.)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
deep-research/
├── app.py                 # Main Gradio application
├── config.py              # Configuration and enums
├── research_manager.py    # Core orchestration logic
├── planner_agent.py       # Search planning agent
├── search_agent.py        # Web search + evaluation
├── fact_checker_agent.py  # Fact verification agent
├── writer_agent.py        # Report generation agent
├── export_utils.py        # Export to MD/HTML
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key |
| `SENDGRID_API_KEY` | ❌ No | For email reports |
| `SENDGRID_FROM_EMAIL` | ❌ No | Verified sender email |

---

## 🛠️ Tech Stack

- **Frontend**: Gradio 4.x
- **AI Framework**: OpenAI Agents SDK
- **Language Model**: GPT-4o-mini
- **Web Search**: OpenAI WebSearchTool

---

## 📝 License

MIT License - feel free to use for personal or commercial projects.

---

## 🙏 Acknowledgments

Built with [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) and [Gradio](https://gradio.app).

---

<div align="center">
Made with ❤️ for researchers and analysts
</div>
