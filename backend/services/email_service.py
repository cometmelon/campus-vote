"""Email service using Resend"""
import logging
from typing import List
from datetime import datetime

import resend

from config import settings
from models import QueueStatus

logger = logging.getLogger(__name__)


def send_voting_emails(db, queue_entries: List, election) -> int:
    """Send voting emails to users in queue"""
    
    sent_count = 0
    
    for entry in queue_entries:
        try:
            voting_url = f"http://localhost:5174/vote/{entry.voting_token}"
            
            if settings.RESEND_API_KEY:
                # Real email sending with Resend
                resend.api_key = settings.RESEND_API_KEY
                
                resend.Emails.send({
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
                    """
                })
            else:
                # Simulation mode - log instead of send
                logger.info(f"[EMAIL SIM] To: {entry.user.email}, Election: {election.title}, Link: {voting_url}")
            
            # Update entry status
            entry.status = QueueStatus.NOTIFIED
            entry.notified_at = datetime.utcnow()
            sent_count += 1
            
        except Exception as e:
            logger.error(f"Failed to send email to {entry.user.email}: {e}")
    
    db.commit()
    return sent_count
