from typing import Dict
from datetime import datetime


def format_email_preview(email: Dict, classification: Dict, summary: Dict) -> str:
    """Format email information for preview"""
    preview = f"""
{'=' * 80}
EMAIL PREVIEW
{'=' * 80}

ID: {email['id']}
From: {email['from']}
Subject: {email['subject']}
Date: {email['date']}

Category: {classification['category'].upper()}
Priority: {classification['priority'].upper()}
Confidence: {classification['confidence']:.2%}

SUMMARY:
{summary['summary']}

KEY POINTS:
{chr(10).join(f"  - {point}" for point in summary.get('key_points', []))}

ACTION ITEMS:
{chr(10).join(f"  - {item}" for item in summary.get('action_items', [])) or "  None"}

SENTIMENT: {summary['sentiment'].upper()}

{'=' * 80}
"""
    return preview


def format_reply_preview(reply: Dict, email: Dict) -> str:
    """Format reply for preview"""
    preview = f"""
{'=' * 80}
DRAFT REPLY
{'=' * 80}

To: {email['from']}
Subject: {reply['subject']}
Tone: {reply['tone'].upper()}
Confidence: {reply['confidence']:.2%}

BODY:
{reply['body']}

{'=' * 80}
"""
    return preview


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level"""
    emojis = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    return emojis.get(priority.lower(), "⚪")


def get_category_emoji(category: str) -> str:
    """Get emoji for category"""
    emojis = {
        "urgent": "⚠️",
        "important": "⭐",
        "promotional": "📢",
        "newsletter": "📰",
        "spam": "🗑️",
        "general": "📧",
    }
    return emojis.get(category.lower(), "📧")


def format_timestamp(iso_timestamp: str = None) -> str:
    """Format ISO timestamp to readable format"""
    if not iso_timestamp:
        dt = datetime.now()
    else:
        dt = datetime.fromisoformat(iso_timestamp)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def extract_email_address(from_field: str) -> str:
    """Extract email address from 'From' field"""
    if "<" in from_field and ">" in from_field:
        return from_field.split("<")[1].split(">")[0].strip()
    return from_field.strip()
