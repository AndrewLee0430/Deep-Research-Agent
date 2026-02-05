"""
Deep Research v2 - Email Agent
改進版郵件發送
"""

import os
from typing import Dict, Optional
from pydantic import BaseModel, Field

try:
    import sendgrid
    from sendgrid.helpers.mail import Email, Mail, Content, To
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

from agents import Agent, function_tool


class EmailResult(BaseModel):
    success: bool
    message: str
    email_address: Optional[str] = None


@function_tool
def send_email(subject: str, html_body: str, to_email: str = None) -> Dict[str, str]:
    """Send an email with the given subject and HTML body"""
    if not SENDGRID_AVAILABLE:
        return {"status": "error", "message": "SendGrid not installed"}
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        return {"status": "error", "message": "SENDGRID_API_KEY not configured"}
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email = Email(os.environ.get('SENDGRID_FROM_EMAIL', 'service@example.com'))
        recipient = To(to_email or os.environ.get('DEFAULT_EMAIL_RECIPIENT', 'user@example.com'))
        content = Content("text/html", html_body)
        mail = Mail(from_email, recipient, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        print(f"Email sent, status: {response.status_code}")
        return {"status": "success", "code": str(response.status_code)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


EMAIL_INSTRUCTIONS = """
You are an email formatting specialist. Convert research reports into professional HTML emails.

Your task:
1. Create a clear, professional subject line (≤80 chars)
   Format: "[Deep Research] <Topic> — Key Findings"

2. Convert Markdown to clean, email-safe HTML with this structure:

   📧 EMAIL STRUCTURE:
   ┌─────────────────────────────────────┐
   │ Opening (1 sentence greeting)       │
   ├─────────────────────────────────────┤
   │ 📋 Executive Summary                │
   │ • 4-7 key bullet points             │
   ├─────────────────────────────────────┤
   │ 💡 Key Insights                     │
   │ Organized sections with h2/h3      │
   ├─────────────────────────────────────┤
   │ 🔍 Recommended Next Steps           │
   │ • Follow-up questions/actions       │
   ├─────────────────────────────────────┤
   │ 📄 Full Report                      │
   │ Complete report (collapsible)       │
   └─────────────────────────────────────┘

3. HTML/CSS Requirements:
   - Inline CSS only (no external stylesheets)
   - System font stack: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
   - Body text: 14-16px, line-height: 1.6
   - Headings: Bold, with consistent sizing
   - Max-width: 600px for readability
   - Light background (#f5f5f5), white content areas
   - Accent color for headers: #2563eb (blue)

4. Preserve:
   - Links (make clickable)
   - Code blocks (<pre><code>)
   - Tables (simple styling)
   - Lists (proper indentation)

Call send_email ONCE with the formatted content.
"""


email_agent = Agent(
    name="EmailAgent",
    instructions=EMAIL_INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
