import os
import base64
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from core.config import settings
from utils.logger import logger

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailClient:
    """Gmail API client wrapper"""

    def __init__(self):
        self.creds = self._authenticate()
        self.service = build("gmail", "v1", credentials=self.creds)

    def _authenticate(self) -> Credentials:
        """Authenticate with Gmail API"""
        creds = None

        if os.path.exists(settings.gmail_token_path):
            creds = Credentials.from_authorized_user_file(
                settings.gmail_token_path, SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.gmail_credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(settings.gmail_token_path, "w") as token:
                token.write(creds.to_json())

        logger.info("Gmail authentication successful")
        return creds

    def fetch_unread_emails(self, max_results: int = 50) -> List[Dict]:
        """Fetch unread emails from inbox"""
        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                email_data = self._get_email_details(message["id"])
                if email_data:
                    emails.append(email_data)

            logger.info(f"Fetched {len(emails)} unread emails")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _get_email_details(self, msg_id: str) -> Optional[Dict]:
        """Get detailed information about a specific email"""
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

            headers = message["payload"]["headers"]
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"), ""
            )
            from_email = next(
                (h["value"] for h in headers if h["name"].lower() == "from"), ""
            )
            date = next(
                (h["value"] for h in headers if h["name"].lower() == "date"), ""
            )

            body = self._get_email_body(message["payload"])

            return {
                "id": msg_id,
                "thread_id": message["threadId"],
                "subject": subject,
                "from": from_email,
                "date": date,
                "body": body,
                "snippet": message.get("snippet", ""),
            }

        except Exception as e:
            logger.error(f"Error getting email details for {msg_id}: {e}")
            return None

    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                            "utf-8"
                        )
                        break
        elif "body" in payload and "data" in payload["body"]:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

        return body

    def send_email(
        self, to: str, subject: str, body: str, thread_id: Optional[str] = None
    ) -> bool:
        """Send an email"""
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            send_data = {"raw": raw_message}
            if thread_id:
                send_data["threadId"] = thread_id

            self.service.users().messages().send(userId="me", body=send_data).execute()

            logger.info(f"Email sent to {to}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def mark_as_read(self, msg_id: str) -> bool:
        """Mark email as read"""
        try:
            self.service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False

    def add_label(self, msg_id: str, label: str) -> bool:
        """Add label to email"""
        try:
            self.service.users().messages().modify(
                userId="me", id=msg_id, body={"addLabelIds": [label]}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding label: {e}")
            return False
