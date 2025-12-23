from typing import Dict, List, Optional
from core.llm_client import get_llm_client
from core.vector_store import vector_store
from utils.logger import logger


class ReplyDrafterAgent:
    """Agent responsible for drafting email replies using RAG"""

    def __init__(self):
        self.system_prompt = """You are a professional email response assistant.
Draft polite, concise, and contextually appropriate email replies.
Match the tone of the incoming email and maintain professionalism."""
        logger.info("Reply Drafter Agent initialized")

    def draft_reply(
        self, email: Dict, classification: Dict, summary: Dict, context: Optional[str] = None
    ) -> Dict:
        """
        Draft a reply to the email using RAG

        Returns:
            {
                'subject': str,
                'body': str,
                'tone': str,
                'confidence': float
            }
        """
        # Search for similar past responses using RAG
        similar_responses = vector_store.search_similar_responses(
            email["body"], n_results=3
        )

        rag_context = self._format_rag_context(similar_responses)

        sender_info = self._extract_sender_name(email["from"])

        additional_context = ("ADDITIONAL CONTEXT:\n" + context) if context else ""

        prompt = f"""Draft a professional email reply based on the following:

INCOMING EMAIL:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

CLASSIFICATION:
Category: {classification['category']}
Priority: {classification['priority']}

SUMMARY:
{summary['summary']}

Key Points: {', '.join(summary.get('key_points', []))}
Action Items: {', '.join(summary.get('action_items', []))}
Sentiment: {summary['sentiment']}

{rag_context}

{additional_context}

Generate a reply in the following JSON format:
{{
    "subject": "Re: original subject",
    "body": "professionally formatted email body",
    "tone": "one of: formal, professional, casual, friendly",
    "confidence": 0.0-1.0
}}

Guidelines:
- Address the sender by name if available: {sender_info['name'] or 'there'}
- Be concise and clear
- Address all key points and action items
- Match the tone of the incoming email
- Include a clear call-to-action if needed
- Sign off appropriately
- If you need more information, ask clarifying questions politely"""

        try:
            result = get_llm_client().generate_json(prompt, system_prompt=self.system_prompt)

            logger.info(f"Drafted reply for email {email['id']}")
            return result

        except Exception as e:
            logger.error(f"Error drafting reply: {e}")
            return {
                "subject": f"Re: {email['subject']}",
                "body": "Thank you for your email. I will review and get back to you shortly.",
                "tone": "professional",
                "confidence": 0.3,
            }

    def _format_rag_context(self, similar_responses: List[Dict]) -> str:
        """Format similar past responses for context"""
        if not similar_responses:
            return ""

        context = "SIMILAR PAST RESPONSES (for reference):\n"
        for i, resp in enumerate(similar_responses, 1):
            context += f"\n{i}. {resp['response'][:200]}...\n"

        return context

    def _extract_sender_name(self, from_field: str) -> Dict:
        """Extract sender name from 'From' field"""
        try:
            if "<" in from_field and ">" in from_field:
                name = from_field.split("<")[0].strip().strip('"')
                email = from_field.split("<")[1].split(">")[0].strip()
            else:
                name = ""
                email = from_field.strip()

            # Extract first name if full name is present
            first_name = name.split()[0] if name else ""

            return {"name": first_name, "full_name": name, "email": email}

        except Exception as e:
            logger.error(f"Error extracting sender name: {e}")
            return {"name": "", "full_name": "", "email": from_field}

    def refine_reply(
        self, original_draft: str, feedback: str, email: Dict
    ) -> Dict:
        """Refine a draft based on user feedback"""
        prompt = f"""Refine the following email reply based on user feedback:

ORIGINAL DRAFT:
{original_draft}

USER FEEDBACK:
{feedback}

ORIGINAL EMAIL CONTEXT:
From: {email['from']}
Subject: {email['subject']}

Generate an improved reply in the following JSON format:
{{
    "subject": "Re: original subject",
    "body": "improved email body",
    "tone": "one of: formal, professional, casual, friendly",
    "confidence": 0.0-1.0
}}"""

        try:
            result = get_llm_client().generate_json(prompt, system_prompt=self.system_prompt)
            logger.info(f"Refined reply for email {email['id']}")
            return result

        except Exception as e:
            logger.error(f"Error refining reply: {e}")
            return {
                "subject": f"Re: {email['subject']}",
                "body": original_draft,
                "tone": "professional",
                "confidence": 0.5,
            }
