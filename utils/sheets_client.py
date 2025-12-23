import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, Any
from core.config import settings
from utils.logger import logger


class SheetsClient:
    """Google Sheets client for logging email activities"""

    def __init__(self):
        try:
            self.client = gspread.oauth(
                credentials_filename=settings.gmail_credentials_path,
                authorized_user_filename=settings.gmail_token_path,
            )

            if settings.google_sheets_id:
                self.sheet = self.client.open_by_key(settings.google_sheets_id)
                self.worksheet = self.sheet.sheet1
                self._ensure_headers()
                logger.info("Google Sheets client initialized")
            else:
                self.sheet = None
                logger.warning("Google Sheets ID not configured")

        except Exception as e:
            logger.error(f"Error initializing Sheets client: {e}")
            self.sheet = None

    def _ensure_headers(self):
        """Ensure the worksheet has proper headers"""
        headers = [
            "Timestamp",
            "Email ID",
            "From",
            "Subject",
            "Category",
            "Priority",
            "Summary",
            "Reply Sent",
            "Reply Time (s)",
            "Follow-up Date",
        ]

        try:
            existing_headers = self.worksheet.row_values(1)
            if not existing_headers or existing_headers != headers:
                self.worksheet.update("A1:J1", [headers])
        except Exception as e:
            logger.error(f"Error setting headers: {e}")

    def log_email_activity(self, data: Dict[str, Any]) -> bool:
        """Log email processing activity to Google Sheets"""
        if not self.sheet:
            return False

        try:
            row = [
                data.get("timestamp", datetime.now().isoformat()),
                data.get("email_id", ""),
                data.get("from", ""),
                data.get("subject", ""),
                data.get("category", ""),
                data.get("priority", ""),
                data.get("summary", ""),
                data.get("reply_sent", "No"),
                data.get("reply_time", ""),
                data.get("follow_up_date", ""),
            ]

            self.worksheet.append_row(row)
            logger.info(f"Logged activity for email: {data.get('email_id')}")
            return True

        except Exception as e:
            logger.error(f"Error logging to Sheets: {e}")
            return False

    def update_reply_status(self, email_id: str, reply_sent: bool, reply_time: float):
        """Update reply status for a specific email"""
        if not self.sheet:
            return False

        try:
            cell = self.worksheet.find(email_id)
            if cell:
                row = cell.row
                self.worksheet.update_cell(row, 8, "Yes" if reply_sent else "No")
                self.worksheet.update_cell(row, 9, f"{reply_time:.2f}")
                return True

        except Exception as e:
            logger.error(f"Error updating reply status: {e}")
            return False


# Global sheets client instance
sheets_client = SheetsClient()
