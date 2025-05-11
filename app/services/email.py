from typing import Optional, List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings
from pathlib import Path
import jinja2
import os

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.EMAILS_FROM_EMAIL,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_FROM_NAME=settings.PROJECT_NAME,
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates' / 'email'
        )
        self.fastmail = FastMail(self.conf)
        self.template_loader = jinja2.FileSystemLoader(
            searchpath=str(Path(__file__).parent.parent / 'templates' / 'email')
        )
        self.template_env = jinja2.Environment(loader=self.template_loader)

    async def send_ticket_assignment_email(
        self,
        email_to: EmailStr,
        ticket_title: str,
        ticket_description: str,
        ticket_id: str,
        assigned_by: str
    ) -> None:
        """Send email notification for ticket assignment"""
        template = self.template_env.get_template('ticket_assignment.html')
        html_content = template.render(
            ticket_title=ticket_title,
            ticket_description=ticket_description,
            ticket_id=ticket_id,
            assigned_by=assigned_by,
            project_name=settings.PROJECT_NAME
        )

        message = MessageSchema(
            subject=f"New Ticket Assigned: {ticket_title}",
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )

        await self.fastmail.send_message(message)

    async def send_ticket_update_email(
        self,
        email_to: EmailStr,
        ticket_title: str,
        ticket_id: str,
        updated_by: str,
        changes: dict
    ) -> None:
        """Send email notification for ticket updates"""
        template = self.template_env.get_template('ticket_update.html')
        html_content = template.render(
            ticket_title=ticket_title,
            ticket_id=ticket_id,
            updated_by=updated_by,
            changes=changes,
            project_name=settings.PROJECT_NAME
        )

        message = MessageSchema(
            subject=f"Ticket Updated: {ticket_title}",
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )

        await self.fastmail.send_message(message)

    async def send_ticket_comment_email(
        self,
        email_to: EmailStr,
        ticket_title: str,
        ticket_id: str,
        comment_by: str,
        comment_content: str
    ) -> None:
        """Send email notification for new comments"""
        template = self.template_env.get_template('ticket_comment.html')
        html_content = template.render(
            ticket_title=ticket_title,
            ticket_id=ticket_id,
            comment_by=comment_by,
            comment_content=comment_content,
            project_name=settings.PROJECT_NAME
        )

        message = MessageSchema(
            subject=f"New Comment on Ticket: {ticket_title}",
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )

        await self.fastmail.send_message(message) 