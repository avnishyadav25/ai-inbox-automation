#!/usr/bin/env python3
"""
AI Inbox Automation Agent Suite
Main orchestrator for the multi-agent email management system
"""

import time
from datetime import datetime
from typing import Dict, List
from agents.fetcher import FetcherAgent
from agents.classifier import ClassifierAgent
from agents.summarizer import SummarizerAgent
from agents.reply_drafter import ReplyDrafterAgent
from agents.scheduler import SchedulerAgent
from core.gmail_client import GmailClient
from core.vector_store import vector_store
from core.config import settings
from utils.sheets_client import sheets_client
from utils.logger import logger
from utils.helpers import (
    format_email_preview,
    format_reply_preview,
    get_priority_emoji,
    get_category_emoji,
)


class InboxAutomationOrchestrator:
    """Main orchestrator for the inbox automation system"""

    def __init__(self):
        logger.info("Initializing Inbox Automation Orchestrator...")

        self.fetcher = FetcherAgent()
        self.classifier = ClassifierAgent()
        self.summarizer = SummarizerAgent()
        self.reply_drafter = ReplyDrafterAgent()
        self.scheduler = SchedulerAgent()
        self.gmail_client = GmailClient()

        logger.info("Orchestrator initialized successfully")

    def process_emails(self):
        """Main email processing pipeline"""
        logger.info("Starting email processing cycle...")

        # Fetch new emails
        emails = self.fetcher.fetch_new_emails()

        if not emails:
            logger.info("No emails to process")
            return

        # Process each email
        for email in emails:
            try:
                self._process_single_email(email)
            except Exception as e:
                logger.error(f"Error processing email {email['id']}: {e}")
                continue

        logger.info(f"Completed processing {len(emails)} emails")

    def _process_single_email(self, email: Dict):
        """Process a single email through the pipeline"""
        start_time = time.time()

        logger.info(f"Processing email: {email['subject']}")

        # Step 1: Classify
        classification = self.classifier.classify_email(email)
        priority_emoji = get_priority_emoji(classification["priority"])
        category_emoji = get_category_emoji(classification["category"])

        print(
            f"\n{priority_emoji} {category_emoji} [{classification['category'].upper()}] "
            f"[{classification['priority'].upper()}] {email['subject']}"
        )

        # Step 2: Summarize
        summary = self.summarizer.summarize_email(email, classification)

        # Step 3: Display preview
        preview = format_email_preview(email, classification, summary)
        print(preview)

        # Step 4: Decide if we should auto-respond
        should_respond = self.classifier.should_auto_respond(classification)

        reply_data = None
        reply_sent = False

        if should_respond:
            # Step 5: Draft reply using RAG
            reply_data = self.reply_drafter.draft_reply(
                email, classification, summary
            )

            reply_preview = format_reply_preview(reply_data, email)
            print(reply_preview)

            # Step 6: Human approval (if required)
            if settings.reply_approval_required:
                approval = self._get_human_approval(email, reply_data)

                if approval == "approve":
                    reply_sent = self._send_reply(email, reply_data)
                elif approval == "edit":
                    feedback = input("Enter your feedback: ").strip()
                    refined_reply = self.reply_drafter.refine_reply(
                        reply_data["body"], feedback, email
                    )
                    reply_sent = self._send_reply(email, refined_reply)
                elif approval == "skip":
                    logger.info(f"Skipped sending reply for email {email['id']}")
            else:
                # Auto-send without approval
                reply_sent = self._send_reply(email, reply_data)

        # Step 7: Schedule follow-up if needed
        follow_up_date = None
        if not reply_sent and classification["priority"] in ["high", "medium"]:
            follow_up_info = self.scheduler.schedule_follow_up(email["id"], email)
            follow_up_date = follow_up_info["follow_up_date"]
            print(f"\n📅 Follow-up scheduled for: {follow_up_date}")

        # Step 8: Store in vector database for RAG
        if reply_sent and reply_data:
            vector_store.add_email_pair(
                email["id"],
                email["body"],
                reply_data["body"],
                metadata={
                    "category": classification["category"],
                    "priority": classification["priority"],
                    "subject": email["subject"],
                },
            )

        # Step 9: Log to Google Sheets
        processing_time = time.time() - start_time

        sheets_client.log_email_activity(
            {
                "timestamp": datetime.now().isoformat(),
                "email_id": email["id"],
                "from": email["from"],
                "subject": email["subject"],
                "category": classification["category"],
                "priority": classification["priority"],
                "summary": summary["summary"],
                "reply_sent": "Yes" if reply_sent else "No",
                "reply_time": f"{processing_time:.2f}",
                "follow_up_date": follow_up_date or "",
            }
        )

        # Step 10: Mark as processed
        self.fetcher.mark_as_processed(email["id"])

        logger.info(
            f"Email {email['id']} processed in {processing_time:.2f} seconds"
        )

    def _get_human_approval(self, email: Dict, reply_data: Dict) -> str:
        """Get human approval for reply"""
        print("\nOptions:")
        print("  [1] Approve and send")
        print("  [2] Edit with feedback")
        print("  [3] Skip")

        while True:
            choice = input("\nYour choice (1/2/3): ").strip()

            if choice == "1":
                return "approve"
            elif choice == "2":
                return "edit"
            elif choice == "3":
                return "skip"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    def _send_reply(self, email: Dict, reply_data: Dict) -> bool:
        """Send email reply"""
        to_email = email["from"]
        subject = reply_data["subject"]
        body = reply_data["body"]
        thread_id = email.get("thread_id")

        success = self.gmail_client.send_email(to_email, subject, body, thread_id)

        if success:
            logger.info(f"Reply sent successfully for email {email['id']}")
            print("\n✅ Reply sent successfully!")
        else:
            logger.error(f"Failed to send reply for email {email['id']}")
            print("\n❌ Failed to send reply")

        return success

    def check_follow_ups(self):
        """Check and process due follow-ups"""
        logger.info("Checking for due follow-ups...")

        due_follow_ups = self.scheduler.get_due_follow_ups()

        if not due_follow_ups:
            logger.info("No due follow-ups")
            return

        print(f"\n📬 {len(due_follow_ups)} follow-up(s) due:")

        for follow_up in due_follow_ups:
            print(f"\n  • {follow_up['subject']}")
            print(f"    From: {follow_up['from']}")
            print(f"    Due: {follow_up['follow_up_date']}")

            choice = input("\n    Mark as completed? (y/n): ").strip().lower()

            if choice == "y":
                self.scheduler.mark_completed(follow_up["email_id"])
                print("    ✅ Marked as completed")
            else:
                print("    ⏭️  Skipped")

    def display_stats(self):
        """Display system statistics"""
        vector_size = vector_store.get_collection_size()
        follow_up_stats = self.scheduler.get_follow_up_stats()

        print("\n" + "=" * 80)
        print("SYSTEM STATISTICS")
        print("=" * 80)
        print(f"Vector Store Size: {vector_size} email pairs")
        print(f"\nFollow-ups:")
        print(f"  Total: {follow_up_stats['total']}")
        print(f"  Pending: {follow_up_stats['pending']}")
        print(f"  Completed: {follow_up_stats['completed']}")
        print(f"  Completion Rate: {follow_up_stats['completion_rate']:.1f}%")
        print("=" * 80 + "\n")

    def run_continuous(self):
        """Run the automation continuously"""
        logger.info("Starting continuous automation mode...")
        print(f"\n🤖 AI Inbox Automation Agent Suite")
        print(f"Checking emails every {settings.email_check_interval} seconds")
        print(f"Press Ctrl+C to stop\n")

        try:
            while True:
                self.process_emails()
                self.check_follow_ups()

                logger.info(
                    f"Waiting {settings.email_check_interval} seconds until next check..."
                )
                time.sleep(settings.email_check_interval)

        except KeyboardInterrupt:
            logger.info("Stopping automation...")
            self.display_stats()
            print("\n👋 Automation stopped")


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("AI INBOX AUTOMATION AGENT SUITE")
    print("=" * 80)

    orchestrator = InboxAutomationOrchestrator()

    print("\nOptions:")
    print("  [1] Process emails once")
    print("  [2] Run continuous automation")
    print("  [3] Check follow-ups")
    print("  [4] Display statistics")
    print("  [5] Exit")

    while True:
        choice = input("\nYour choice (1-5): ").strip()

        if choice == "1":
            orchestrator.process_emails()
        elif choice == "2":
            orchestrator.run_continuous()
        elif choice == "3":
            orchestrator.check_follow_ups()
        elif choice == "4":
            orchestrator.display_stats()
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
