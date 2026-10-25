from rgb_website.config import Settings
from rgb_website.services import NotificationService


class RecordingSender:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def send(self, recipient: str, subject: str, body: str) -> None:
        self.calls.append((recipient, subject, body))


def test_incomplete_enabled_notification_configuration_is_skipped(db_session) -> None:
    sender = RecordingSender()
    settings = Settings(
        notification_enabled=True,
        smtp_from="study@example.invalid",
        notification_operator_recipient="operator@example.invalid",
        notification_technical_recipient="technical@example.invalid",
    )

    NotificationService(db_session, settings, sender).notify_completed_participation()

    assert sender.calls == []
