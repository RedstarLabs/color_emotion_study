import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from rgb_website.config import Settings
from rgb_website.repositories import SurveySessionRepository

logger = logging.getLogger(__name__)

SUBJECT = "Neue Teilnahme – Farb-Emotions-Studie"


class EmailSender(Protocol):
    def send(self, recipient: str, subject: str, body: str) -> None:
        ...


class SMTPEmailSender:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.settings.smtp_from
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        smtp_class = smtplib.SMTP_SSL if self.settings.smtp_use_ssl else smtplib.SMTP
        with smtp_class(
            self.settings.smtp_host,
            self.settings.smtp_port,
            timeout=self.settings.smtp_timeout,
        ) as smtp:
            if self.settings.smtp_starttls:
                smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)


class NotificationService:
    def __init__(
        self,
        db: Session,
        settings: Settings,
        sender: EmailSender | None = None,
    ) -> None:
        self.sessions = SurveySessionRepository(db)
        self.settings = settings
        self.sender = sender or SMTPEmailSender(settings)

    def notify_completed_participation(self) -> None:
        if not self.settings.notification_enabled:
            return
        if not self._is_configured():
            logger.warning(
                "Completion notification is enabled but SMTP configuration "
                "is incomplete."
            )
            return

        try:
            completed_count = self.sessions.count_completed()
        except SQLAlchemyError:
            logger.exception(
                "Could not count completed participations for notification."
            )
            return

        body = (
            "Eine weitere Person hat die Farb-Emotions-Studie vollständig "
            "abgeschlossen.\n\n"
            f"Abgeschlossene Teilnahmen insgesamt: {completed_count}"
        )
        for recipient in self._recipients():
            try:
                self.sender.send(recipient, SUBJECT, body)
            except (ValueError, OSError, smtplib.SMTPException) as error:
                logger.error(
                    "Could not send completion notification (error_type=%s).",
                    type(error).__name__,
                )
            except Exception as error:
                logger.error(
                    "Unexpected completion notification failure "
                    "(error_type=%s).",
                    type(error).__name__,
                )

    def _is_configured(self) -> bool:
        required = (
            self.settings.smtp_host,
            self.settings.smtp_from,
            self.settings.notification_operator_recipient,
            self.settings.notification_technical_recipient,
        )
        if not all(required):
            return False
        return (self.settings.smtp_username is None) == (
            self.settings.smtp_password is None
        )

    def _recipients(self) -> tuple[str, str]:
        operator = self.settings.notification_operator_recipient
        technical = self.settings.notification_technical_recipient
        assert operator is not None
        assert technical is not None
        return operator, technical
