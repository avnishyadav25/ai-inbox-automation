from typing import Dict
from core.llm_client import get_llm_client
from utils.logger import logger


class SummarizerAgent:
    """Agent responsible for summarizing email content"""

    def __init__(self):
        self.system_prompt = """You are an expert email summarization assistant.
Create concise, actionable summaries that capture key information and required actions."""
        logger.info("Summarizer Agent initialized")

    def summarize_email(self, email: Dict, classification: Dict) -> Dict:
        """
        Generate a concise summary of the email

        Returns:
            {
                'summary': str,
                'key_points': List[str],
                'action_items': List[str],
                'sentiment': str
            }
        """
        prompt = f"""Summarize the following email concisely:

From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Category: {classification['category']}
Priority: {classification['priority']}

Provide a summary in the following JSON format:
{{
    "summary": "2-3 sentence summary",
    "key_points": ["point 1", "point 2", "point 3"],
    "action_items": ["action 1", "action 2"],
    "sentiment": "one of: positive, neutral, negative, urgent"
}}

Focus on:
- Main purpose of the email
- Important details or requests
- Any deadlines or time constraints
- Action items or required responses"""

        try:
            result = get_llm_client().generate_json(prompt, system_prompt=self.system_prompt)

            logger.info(f"Summarized email {email['id']}")
            return result

        except Exception as e:
            logger.error(f"Error summarizing email: {e}")
            return {
                "summary": email.get("snippet", "Unable to generate summary"),
                "key_points": [],
                "action_items": [],
                "sentiment": "neutral",
            }

    def extract_sender_info(self, from_field: str) -> Dict:
        """Extract name and email from 'From' field"""
        try:
            if "<" in from_field and ">" in from_field:
                name = from_field.split("<")[0].strip().strip('"')
                email = from_field.split("<")[1].split(">")[0].strip()
            else:
                name = ""
                email = from_field.strip()

            return {"name": name, "email": email}

        except Exception as e:
            logger.error(f"Error extracting sender info: {e}")
            return {"name": "", "email": from_field}
