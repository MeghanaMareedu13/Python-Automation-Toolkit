"""
Email Automator - Automated email sending with templates
Part of Python Automation Toolkit | Day 2 of 30-Day Challenge

Demonstrates email automation for notifications, reports,
and bulk communications - key enterprise automation skill.

Author: Meghana Mareedu
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import csv
import re


class EmailAutomator:
    """
    Automated email sending system with templates and attachments.
    
    Features:
    - HTML and plain text emails
    - Template system with variable substitution
    - Bulk sending from CSV
    - Attachment support
    - Email validation
    - Dry-run mode for testing
    """
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587,
                 username: str = None, password: str = None):
        """
        Initialize email configuration.
        
        For demo purposes, actual sending is simulated.
        In production, provide real SMTP credentials.
        """
        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sent_log = []
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def create_template(self, subject: str, body: str, is_html: bool = False) -> Dict:
        """
        Create an email template.
        
        Use {variable_name} for placeholders.
        
        Example:
            subject = "Welcome, {name}!"
            body = "Hello {name}, your order #{order_id} is confirmed."
        """
        return {
            'subject': subject,
            'body': body,
            'is_html': is_html
        }
    
    def fill_template(self, template: Dict, variables: Dict) -> Dict:
        """Fill template placeholders with actual values."""
        filled = template.copy()
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            filled['subject'] = filled['subject'].replace(placeholder, str(value))
            filled['body'] = filled['body'].replace(placeholder, str(value))
        return filled
    
    def send_email(self, to: str, subject: str, body: str,
                   is_html: bool = False, attachments: List[str] = None,
                   dry_run: bool = True) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            is_html: Whether body is HTML
            attachments: List of file paths to attach
            dry_run: If True, simulate sending without actual send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_email(to):
            print(f"❌ Invalid email address: {to}")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.username or "sender@example.com"
        msg['To'] = to
        msg['Subject'] = subject
        
        # Attach body
        mime_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, mime_type))
        
        # Handle attachments
        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if path.exists():
                    with open(path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                       f'attachment; filename="{path.name}"')
                        msg.attach(part)
        
        if dry_run:
            # Simulate sending
            print(f"📧 [DRY RUN] Would send email to: {to}")
            print(f"   Subject: {subject}")
            print(f"   Body preview: {body[:100]}...")
            self._log_sent(to, subject, "DRY_RUN")
            return True
        
        # Actual sending (requires valid SMTP credentials)
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            print(f"✅ Email sent to: {to}")
            self._log_sent(to, subject, "SENT")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            self._log_sent(to, subject, f"FAILED: {e}")
            return False
    
    def send_bulk(self, recipients: List[Dict], template: Dict,
                  dry_run: bool = True) -> Dict:
        """
        Send bulk emails using a template.
        
        Args:
            recipients: List of dicts with 'email' and template variables
            template: Email template with placeholders
            dry_run: Simulate sending
            
        Returns:
            Summary of sent/failed emails
        """
        results = {'sent': 0, 'failed': 0, 'details': []}
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Sending bulk emails...")
        print("=" * 50)
        
        for recipient in recipients:
            email = recipient.get('email')
            if not email:
                continue
            
            # Fill template with recipient's data
            filled = self.fill_template(template, recipient)
            
            success = self.send_email(
                to=email,
                subject=filled['subject'],
                body=filled['body'],
                is_html=filled['is_html'],
                dry_run=dry_run
            )
            
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'email': email,
                'status': 'sent' if success else 'failed'
            })
        
        print(f"\n📊 Summary: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def send_from_csv(self, csv_path: str, template: Dict,
                      email_column: str = 'email', dry_run: bool = True) -> Dict:
        """
        Send emails to recipients from a CSV file.
        
        Args:
            csv_path: Path to CSV file
            template: Email template
            email_column: Column name containing email addresses
            dry_run: Simulate sending
        """
        recipients = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if email_column in row:
                    row['email'] = row[email_column]
                recipients.append(row)
        
        return self.send_bulk(recipients, template, dry_run)
    
    def _log_sent(self, to: str, subject: str, status: str) -> None:
        """Log sent email."""
        self.sent_log.append({
            'timestamp': datetime.now().isoformat(),
            'to': to,
            'subject': subject,
            'status': status
        })
    
    def get_log(self) -> List[Dict]:
        """Get the email send log."""
        return self.sent_log


# Demo usage
if __name__ == "__main__":
    print("📧 Email Automator Demo")
    print("=" * 50)
    
    # Initialize (without real credentials for demo)
    automator = EmailAutomator()
    
    # Create a welcome email template
    welcome_template = automator.create_template(
        subject="Welcome to Our Platform, {name}!",
        body="""
        <html>
        <body>
            <h1>Welcome, {name}! 🎉</h1>
            <p>Thank you for joining us. Your account has been activated.</p>
            <p>Your username: <strong>{username}</strong></p>
            <p>Get started by visiting your dashboard.</p>
            <br>
            <p>Best regards,<br>The Team</p>
        </body>
        </html>
        """,
        is_html=True
    )
    
    # Sample recipients
    recipients = [
        {'email': 'john@example.com', 'name': 'John Doe', 'username': 'johnd'},
        {'email': 'jane@example.com', 'name': 'Jane Smith', 'username': 'janes'},
        {'email': 'invalid-email', 'name': 'Invalid', 'username': 'invalid'},  # Will fail validation
    ]
    
    # Send bulk emails (dry run)
    print("\n📨 Sending Welcome Emails (Dry Run):")
    results = automator.send_bulk(recipients, welcome_template, dry_run=True)
    
    # Show log
    print("\n📋 Email Log:")
    for log in automator.get_log():
        print(f"  {log['timestamp']}: {log['to']} - {log['status']}")
    
    print("\n🎉 Email Automator Demo Complete!")
