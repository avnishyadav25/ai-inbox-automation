from typing import Dict
from core.llm_client import llm_client
from core.config import settings
from utils.logger import logger


class ClassifierAgent:
    """Agent responsible for classifying and prioritizing emails"""

    def __init__(self):
        self.system_prompt = """You are an expert email classification assistant.
Your task is to analyze emails and categorize them accurately."""
        logger.info("Classifier Agent initialized")

    def classify_email(self, email: Dict) -> Dict:
        """
        Classify email by category and priority

        Returns:
            {
                'category': str (urgent, important, promotional, newsletter, spam, general),
                'priority': str (high, medium, low),
                'confidence': float,
                'reasoning': str
            }
        """
        prompt = f"""Analyze the following email and classify it:

From: {email['from']}
Subject: {email['subject']}
Body: {email['body'][:500]}...

Provide classification in the following JSON format:
{{
    "category": "one of: urgent, important, promotional, newsletter, spam, general",
    "priority": "one of: high, medium, low",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Categories:
- urgent: Time-sensitive, requires immediate action
- important: From key contacts, business-critical
- promotional: Marketing, advertisements, offers
- newsletter: Subscriptions, updates, digests
- spam: Unwanted, suspicious
- general: Everything else

Priority:
- high: Action needed within 24h
- medium: Action needed within a week
- low: FYI, no action required"""

        try:
            result = llm_client.generate_json(prompt, system_prompt=self.system_prompt)

            logger.info(
                f"Classified email {email['id']}: {result['category']} - {result['priority']}"
            )
            return result

        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return {
                "category": "general",
                "priority": "medium",
                "confidence": 0.5,
                "reasoning": "Classification failed, using defaults",
            }

    def should_auto_respond(self, classification: Dict) -> bool:
        """Determine if email should get an automatic response"""
        # Don't auto-respond to spam, promotional, or newsletter emails
        no_response_categories = ["spam", "promotional", "newsletter"]

        if classification["category"] in no_response_categories:
            return False

        # Only auto-respond to medium and high priority
        if classification["priority"] == "low":
            return False

        return True

    def get_priority_score(self, classification: Dict) -> float:
        """Get numeric priority score for sorting"""
        priority_scores = {"high": 1.0, "medium": 0.5, "low": 0.1}

        return priority_scores.get(classification["priority"], 0.5)
