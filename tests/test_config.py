from rgb_website.config import Settings


def test_settings_can_be_loaded_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")

    settings = Settings()

    assert settings.app_env == "test"
    assert settings.app_port == 9000
    assert settings.database_url == "sqlite:///./test.db"


def test_production_rejects_relative_sqlite_path() -> None:
    import pytest

    with pytest.raises(ValueError, match="absolute path"):
        Settings(
            app_env="production",
            database_url="sqlite:///./coloremotionstudy.db",
            admin_api_token="x" * 32,
        )


def test_production_requires_strong_admin_token() -> None:
    import pytest

    with pytest.raises(ValueError, match="32 characters"):
        Settings(
            app_env="production",
            database_url="sqlite:////var/lib/rgb-website/study.db",
            admin_api_token="too-short",
        )


def test_production_accepts_absolute_sqlite_path() -> None:
    settings = Settings(
        app_env="production",
        database_url="sqlite:////var/lib/rgb-website/study.db",
        admin_api_token="x" * 32,
    )

    assert settings.database_url == "sqlite:////var/lib/rgb-website/study.db"


def test_production_rejects_unsupported_sqlite_url_variants() -> None:
    import pytest

    for database_url in (
        "sqlite:///relative.db",
        "sqlite:///:memory:",
        "sqlite+pysqlite:////var/lib/rgb-website/study.db",
        "sqlite:////var/lib/rgb-website/study.db?mode=ro",
        "sqlite:////var/lib/rgb-website/study.db#fragment",
    ):
        with pytest.raises(ValueError, match="SQLite DATABASE_URL"):
            Settings(
                app_env="production",
                database_url=database_url,
                admin_api_token="x" * 32,
            )


def test_notifications_are_disabled_and_unconfigured_by_default() -> None:
    settings = Settings()

    assert settings.notification_enabled is False
    assert settings.smtp_host is None
    assert settings.notification_operator_recipient is None
    assert settings.notification_technical_recipient is None


def test_smtp_ssl_and_starttls_cannot_be_enabled_together() -> None:
    import pytest

    with pytest.raises(ValueError, match="SSL and STARTTLS"):
        Settings(smtp_use_ssl=True, smtp_starttls=True)
