import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.config import settings
import logging
from datetime import date

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from
    
    def _create_absence_email(
        self, 
        student_name: str, 
        absence_date: date, 
        subject_name: str = None
    ) -> MIMEMultipart:
        """Create an absence notification email."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Absence Notification - {settings.app_name}"
        msg['From'] = self.email_from
        
        subject_text = f" for {subject_name}" if subject_name else ""
        
        text_content = f"""
Dear {student_name},

This is to notify you that you were marked absent{subject_text} on {absence_date.strftime('%B %d, %Y')}.

If you believe this is an error, please contact your teacher.

Best regards,
{settings.app_name} Team
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4A90D9; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{settings.app_name}</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{student_name}</strong>,</p>
            <p>This is to notify you that you were marked <strong>absent</strong>{subject_text} on <strong>{absence_date.strftime('%B %d, %Y')}</strong>.</p>
            <p>If you believe this is an error, please contact your teacher.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>{settings.app_name} Team</p>
        </div>
    </div>
</body>
</html>
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        return msg
    
    def send_absence_notification(
        self, 
        to_email: str, 
        student_name: str, 
        absence_date: date,
        subject_name: str = None
    ) -> bool:
        """Send an absence notification email to a student."""
        try:
            msg = self._create_absence_email(student_name, absence_date, subject_name)
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Absence notification sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_bulk_absence_notifications(
        self, 
        students: List[dict], 
        absence_date: date,
        subject_name: str = None
    ) -> dict:
        """
        Send absence notifications to multiple students.
        
        Args:
            students: List of dicts with 'email' and 'name' keys
            absence_date: Date of absence
            subject_name: Optional subject name
            
        Returns:
            Dict with 'success' and 'failed' counts
        """
        results = {"success": 0, "failed": 0}
        
        for student in students:
            if self.send_absence_notification(
                student['email'], 
                student['name'], 
                absence_date,
                subject_name
            ):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results


# Global instance
email_service = EmailService()
