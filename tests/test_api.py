from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from rgb_website.database.base import Base
from rgb_website.database.session import get_db
from rgb_website.main import create_app


def test_health_endpoint_does_not_expose_configuration() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_rejects_unmigrated_database() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    app = create_app()

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    response = TestClient(app).get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Application dependencies are not ready."}
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_start_requires_all_confirmations() -> None:
    response = TestClient(create_app()).post(
        "/api/experiments",
        json={
            "age_confirmed": True,
            "information_acknowledged": True,
            "participation_consent": False,
        },
    )

    assert response.status_code == 422


def test_start_without_request_body_is_rejected() -> None:
    response = TestClient(create_app()).post("/api/experiments")

    assert response.status_code == 422


def test_readiness_accepts_expected_migration_revision() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
        )
        connection.execute(
            text(
                "INSERT INTO alembic_version (version_num) "
                "VALUES ('0005_session_gender')"
            )
        )

    app = create_app()

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    Base.metadata.drop_all(engine)
    engine.dispose()
