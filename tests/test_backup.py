import sqlite3
import subprocess
from pathlib import Path

BACKUP_SCRIPT = Path(__file__).parents[1] / "deploy" / "backup.sh"


def sqlite_cli_environment(tmp_path: Path) -> dict[str, str]:
    fake_bin = tmp_path / "sqlite-bin"
    fake_bin.mkdir(exist_ok=True)
    fake_sqlite = fake_bin / "sqlite3"
    fake_sqlite.write_text(
        """#!/usr/bin/env python3
import sqlite3
import sys

database, command = sys.argv[1:]
if not command.startswith(".backup '") or not command.endswith("'"):
    raise SystemExit(2)
destination = command[len(".backup '"):-1]
with sqlite3.connect(database) as source:
    with sqlite3.connect(destination) as target:
        source.backup(target)
"""
    )
    fake_sqlite.chmod(0o700)
    return {"PATH": f"{fake_bin}:/usr/bin:/bin"}


def make_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE values_table (value TEXT NOT NULL)")
        connection.execute("INSERT INTO values_table VALUES ('temporary')")


def run_backup(
    database: Path,
    backup_directory: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/bash", str(BACKUP_SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        env={
            **environment,
            "DATABASE_PATH": str(database),
            "BACKUP_DIRECTORY": str(backup_directory),
        },
    )


def test_backup_creates_restrictive_backup_and_directory(
    tmp_path: Path,
) -> None:
    database = tmp_path / "study.db"
    backup_directory = tmp_path / "backups"
    make_database(database)

    result = run_backup(database, backup_directory, sqlite_cli_environment(tmp_path))

    assert result.returncode == 0
    assert backup_directory.stat().st_mode & 0o777 == 0o700
    backups = list(backup_directory.glob("*.db"))
    assert len(backups) == 1
    assert backups[0].stat().st_mode & 0o777 == 0o600


def test_backup_rejects_symlink_database(tmp_path: Path) -> None:
    database = tmp_path / "study.db"
    real_database = tmp_path / "real-study.db"
    backup_directory = tmp_path / "backups"
    make_database(real_database)
    database.symlink_to(real_database)

    result = run_backup(database, backup_directory, sqlite_cli_environment(tmp_path))

    assert result.returncode != 0
    assert not backup_directory.exists()


def test_backup_rejects_symlink_directory(tmp_path: Path) -> None:
    database = tmp_path / "study.db"
    real_directory = tmp_path / "real-backups"
    backup_directory = tmp_path / "backups"
    make_database(database)
    real_directory.mkdir()
    backup_directory.symlink_to(real_directory, target_is_directory=True)

    result = run_backup(database, backup_directory, sqlite_cli_environment(tmp_path))

    assert result.returncode != 0
    assert not list(real_directory.iterdir())


def test_backup_rejects_missing_database_and_directory_file(
    tmp_path: Path,
) -> None:
    missing_database = tmp_path / "missing.db"
    backup_directory = tmp_path / "backups"
    result = run_backup(
        missing_database,
        backup_directory,
        sqlite_cli_environment(tmp_path),
    )
    assert result.returncode != 0
    assert not backup_directory.exists()

    database = tmp_path / "study.db"
    make_database(database)
    backup_directory.write_text("not a directory")
    result = run_backup(database, backup_directory, sqlite_cli_environment(tmp_path))
    assert result.returncode != 0
