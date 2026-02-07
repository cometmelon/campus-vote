"""Email service using Resend"""

import logging
from typing import List
from datetime import datetime

import resend

from sqlalchemy.orm import joinedload

from config import settings
from database import SessionLocal
from models import Election, VotingQueue, QueueStatus

logger = logging.getLogger(__name__)


def send_voting_emails_bg(election_id, batch_number: int):
    """Background task to send voting emails"""
    from datetime import datetime

    db = SessionLocal()
    try:
        election = db.query(Election).filter(Election.id == election_id).first()
        if not election:
            logger.error(f"Election {election_id} not found for email sending")
            return

        queue_entries = (
            db.query(VotingQueue)
            .options(joinedload(VotingQueue.user))
            .filter(
                VotingQueue.election_id == election_id,
                VotingQueue.batch_number == batch_number,
                # We don't filter by PENDING strictly because the caller might have just created them.
                # But normally we should only send if not already notified.
                # Let's filter by PENDING or allow re-sending? The original code didn't check status inside the loop but updated it.
                # But the caller usually passes newly created entries.
            )
            .all()
        )

        # Filter for those not yet notified to avoid duplicates if task runs twice?
        # The original code just iterates whatever is passed.
        # Let's stick to processing all entries in the batch that are PENDING.
        queue_entries = [e for e in queue_entries if e.status == QueueStatus.PENDING]

        sent_count = 0
        for entry in queue_entries:
            try:
                voting_url = f"http://localhost:5174/vote/{entry.voting_token}"

                if settings.RESEND_API_KEY:
                    # Real email sending with Resend
                    import resend

                    resend.api_key = settings.RESEND_API_KEY

                    resend.Emails.send(
                        {
                            "from": settings.FROM_EMAIL,
                            "to": entry.user.email,
                            "subject": f"Vote Now: {election.title}",
                            "html": f"""
                        <h2>Your Vote Matters!</h2>
                        <p>You have been invited to vote in: <strong>{election.title}</strong></p>
                        <p>Click the link below to cast your vote:</p>
                        <a href="{voting_url}" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:6px;">
                            Vote Now
                        </a>
                        <p><small>This link expires in 24 hours.</small></p>
                        """,
                        }
                    )
                else:
                    # Simulation mode - log instead of send
                    logger.info(
                        f"[EMAIL SIM] To: {entry.user.email}, Election: {election.title}, Link: {voting_url}"
                    )

                # Update entry status
                entry.status = QueueStatus.NOTIFIED
                entry.notified_at = datetime.utcnow()
                sent_count += 1

            except Exception as e:
                logger.error(f"Failed to send email to {entry.user.email}: {e}")

        db.commit()
        logger.info(
            f"Background email task: Sent {sent_count} emails for election {election.title} batch {batch_number}"
        )

    except Exception as e:
        logger.error(f"Error in background email task: {e}")
    finally:
        db.close()


def send_voting_emails(db, queue_entries: List, election) -> int:
    """Send voting emails to users in queue (Synchronous - Deprecated for direct use)"""
    from datetime import datetime
    from models import QueueStatus

    sent_count = 0

    for entry in queue_entries:
        try:
            voting_url = f"http://localhost:5174/vote/{entry.voting_token}"

            if settings.RESEND_API_KEY:
                # Real email sending with Resend
                import resend

                resend.api_key = settings.RESEND_API_KEY

                resend.Emails.send(
                    {
                        "from": settings.FROM_EMAIL,
                        "to": entry.user.email,
                        "subject": f"Vote Now: {election.title}",
                        "html": f"""
                    <h2>Your Vote Matters!</h2>
                    <p>You have been invited to vote in: <strong>{election.title}</strong></p>
                    <p>Click the link below to cast your vote:</p>
                    <a href="{voting_url}" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:6px;">
                        Vote Now
                    </a>
                    <p><small>This link expires in 24 hours.</small></p>
                    """,
                    }
                )
            else:
                # Simulation mode - log instead of send
                logger.info(
                    f"[EMAIL SIM] To: {entry.user.email}, Election: {election.title}, Link: {voting_url}"
                )

            # Update entry status
            entry.status = QueueStatus.NOTIFIED
            entry.notified_at = datetime.utcnow()
            sent_count += 1

        except Exception as e:
            logger.error(f"Failed to send email to {entry.user.email}: {e}")

    db.commit()
    return sent_count


def send_voting_emails_bg(queue_entry_ids: List[UUID], election_id: UUID):
    """Background task to send voting emails"""
    from models import VotingQueue, Election

    db = SessionLocal()
    try:
        election = db.query(Election).filter(Election.id == election_id).first()
        if not election:
            logger.error(f"Election {election_id} not found in background task")
            return

        queue_entries = db.query(VotingQueue).filter(VotingQueue.id.in_(queue_entry_ids)).all()
        logger.info(f"Processing background email task for {len(queue_entries)} entries")
        send_voting_emails(db, queue_entries, election)
    except Exception as e:
        logger.error(f"Background email task failed: {e}")
    finally:
        db.close()
