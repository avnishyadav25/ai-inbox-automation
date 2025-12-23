from typing import Dict, List
from datetime import datetime, timedelta
import json
import os
from core.config import settings
from utils.logger import logger


class SchedulerAgent:
    """Agent responsible for scheduling follow-ups"""

    def __init__(self, storage_path: str = "./data/follow_ups.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.follow_ups = self._load_follow_ups()
        logger.info("Scheduler Agent initialized")

    def _load_follow_ups(self) -> Dict:
        """Load follow-ups from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading follow-ups: {e}")
                return {}
        return {}

    def _save_follow_ups(self):
        """Save follow-ups to storage"""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.follow_ups, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving follow-ups: {e}")

    def schedule_follow_up(
        self, email_id: str, email_data: Dict, days_until: int = None
    ) -> Dict:
        """
        Schedule a follow-up for an email

        Returns:
            {
                'follow_up_date': str,
                'scheduled': bool
            }
        """
        if days_until is None:
            days_until = settings.follow_up_days

        follow_up_date = datetime.now() + timedelta(days=days_until)

        self.follow_ups[email_id] = {
            "email_id": email_id,
            "subject": email_data.get("subject", ""),
            "from": email_data.get("from", ""),
            "follow_up_date": follow_up_date.isoformat(),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
        }

        self._save_follow_ups()

        logger.info(
            f"Scheduled follow-up for email {email_id} on {follow_up_date.date()}"
        )

        return {
            "follow_up_date": follow_up_date.isoformat(),
            "scheduled": True,
        }

    def get_due_follow_ups(self) -> List[Dict]:
        """Get all follow-ups that are due"""
        now = datetime.now()
        due_follow_ups = []

        for email_id, follow_up in self.follow_ups.items():
            if follow_up["status"] == "pending":
                follow_up_date = datetime.fromisoformat(follow_up["follow_up_date"])
                if follow_up_date <= now:
                    due_follow_ups.append(follow_up)

        logger.info(f"Found {len(due_follow_ups)} due follow-ups")
        return due_follow_ups

    def mark_completed(self, email_id: str):
        """Mark a follow-up as completed"""
        if email_id in self.follow_ups:
            self.follow_ups[email_id]["status"] = "completed"
            self.follow_ups[email_id]["completed_at"] = datetime.now().isoformat()
            self._save_follow_ups()
            logger.info(f"Marked follow-up {email_id} as completed")

    def cancel_follow_up(self, email_id: str):
        """Cancel a scheduled follow-up"""
        if email_id in self.follow_ups:
            del self.follow_ups[email_id]
            self._save_follow_ups()
            logger.info(f"Cancelled follow-up for email {email_id}")

    def get_all_follow_ups(self) -> Dict:
        """Get all scheduled follow-ups"""
        return self.follow_ups

    def get_follow_up_stats(self) -> Dict:
        """Get statistics about follow-ups"""
        total = len(self.follow_ups)
        pending = sum(1 for f in self.follow_ups.values() if f["status"] == "pending")
        completed = sum(
            1 for f in self.follow_ups.values() if f["status"] == "completed"
        )

        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
        }
