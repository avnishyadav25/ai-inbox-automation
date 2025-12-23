from typing import List, Dict
from core.gmail_client import GmailClient
from core.config import settings
from utils.logger import logger


class FetcherAgent:
    """Agent responsible for fetching emails from Gmail"""

    def __init__(self):
        self.gmail_client = GmailClient()
        logger.info("Fetcher Agent initialized")

    def fetch_new_emails(self) -> List[Dict]:
        """
        Fetch new unread emails from inbox

        Returns:
            List of email dictionaries with structure:
            {
                'id': str,
                'thread_id': str,
                'subject': str,
                'from': str,
                'date': str,
                'body': str,
                'snippet': str
            }
        """
        logger.info("Fetching new emails...")
        emails = self.gmail_client.fetch_unread_emails(
            max_results=settings.max_emails_per_run
        )

        if emails:
            logger.info(f"Successfully fetched {len(emails)} unread emails")
        else:
            logger.info("No unread emails found")

        return emails

    def mark_as_processed(self, email_id: str) -> bool:
        """Mark email as read after processing"""
        return self.gmail_client.mark_as_read(email_id)

    def get_email_by_id(self, email_id: str) -> Dict:
        """Fetch a specific email by ID"""
        return self.gmail_client._get_email_details(email_id)
