import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

RESTORE_SCRIPT = Path(__file__).parents[1] / "deploy" / "restore.sh"


def sqlite_cli_environment(tmp_path: Path) -> dict[str, str]:
    fake_bin = tmp_path / "sqlite-bin"
    fake_bin.mkdir(exist_ok=True)
    fake_sqlite = fake_bin / "sqlite3"
    fake_sqlite.write_text(
        """#!/usr/bin/env python3
import sqlite3
import sys

arguments = sys.argv[1:]
if arguments and arguments[0] == "-batch":
    arguments.pop(0)
database, command = arguments
if command == "PRAGMA integrity_check;":
    with sqlite3.connect(database) as connection:
        for (result,) in connection.execute(command):
            print(result)
elif command.startswith(".backup '") and command.endswith("'"):
    destination = command[len(".backup '"):-1]
    with sqlite3.connect(database) as source:
        with sqlite3.connect(destination) as target:
            source.backup(target)
else:
    raise SystemExit(2)
"""
    )
    fake_sqlite.chmod(0o700)
    return {"PATH": f"{fake_bin}:/usr/bin:/bin"}


def make_database(path: Path, *, corrupt: bool = False) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE values_table (value TEXT NOT NULL)")
        connection.execute("INSERT INTO values_table VALUES ('temporary')")
    if corrupt:
        with path.open("r+b") as database:
            database.seek(0)
            database.write(b"not a sqlite database")


def run_restore(
    source: Path,
    target: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(RESTORE_SCRIPT), str(source), str(target)],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )


def test_restore_creates_database_with_restrictive_permissions(tmp_path: Path) -> None:
    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    make_database(source)

    result = run_restore(source, target, sqlite_cli_environment(tmp_path))

    assert result.returncode == 0
    assert target.exists()
    assert target.stat().st_mode & 0o777 == 0o600
    with sqlite3.connect(target) as connection:
        assert connection.execute("SELECT * FROM values_table").fetchone() == (
            "temporary",
        )


def test_restore_uses_real_sqlite_cli_when_available(tmp_path: Path) -> None:
    sqlite3_cli = shutil.which("sqlite3")
    if sqlite3_cli is None:
        pytest.skip("sqlite3 CLI is not installed")

    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    make_database(source)

    result = run_restore(
        source,
        target,
        {"PATH": f"{Path(sqlite3_cli).parent}:/usr/bin:/bin"},
    )

    assert result.returncode == 0
    with sqlite3.connect(target) as connection:
        assert connection.execute("SELECT * FROM values_table").fetchone() == (
            "temporary",
        )


def test_restore_rejects_invalid_source_without_target(tmp_path: Path) -> None:
    source = tmp_path / "corrupt.db"
    target = tmp_path / "restored.db"
    make_database(source, corrupt=True)

    result = run_restore(source, target, sqlite_cli_environment(tmp_path))

    assert result.returncode != 0
    assert "could not be checked" in result.stderr
    assert not target.exists()


def test_restore_rejects_existing_target_and_symlink(tmp_path: Path) -> None:
    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    make_database(source)
    target.write_bytes(b"keep")

    result = run_restore(source, target, sqlite_cli_environment(tmp_path))

    assert result.returncode != 0
    assert target.read_bytes() == b"keep"

    target.unlink()
    target.symlink_to(source)
    result = run_restore(source, target, sqlite_cli_environment(tmp_path))
    assert result.returncode != 0
    assert target.is_symlink()


def test_restore_rejects_identical_source_and_target(tmp_path: Path) -> None:
    source = tmp_path / "backup.db"
    make_database(source)

    result = run_restore(source, source, sqlite_cli_environment(tmp_path))

    assert result.returncode != 0
    assert "different files" in result.stderr


def test_restore_rejects_relative_or_missing_paths(tmp_path: Path) -> None:
    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    environment = sqlite_cli_environment(tmp_path)

    missing = run_restore(source, target, environment)
    assert missing.returncode == 2

    relative = subprocess.run(
        [str(RESTORE_SCRIPT), "backup.db", str(target)],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    assert relative.returncode == 2


def test_restore_leaves_no_partial_target_after_failed_backup(
    tmp_path: Path,
) -> None:
    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    make_database(source)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_sqlite = fake_bin / "sqlite3"
    fake_sqlite.write_text(
        "#!/usr/bin/env bash\n"
        'if [[ "$*" == *"PRAGMA integrity_check"* ]]; then\n'
        "  printf 'ok\\n'\n"
        "  exit 0\n"
        "fi\n"
        "exit 1\n"
    )
    fake_sqlite.chmod(0o700)
    result = run_restore(source, target, {"PATH": f"{fake_bin}:/usr/bin:/bin"})

    assert result.returncode != 0
    assert not target.exists()
    assert not list(tmp_path.glob(".restore.*"))


def test_restore_leaves_no_files_when_setting_permissions_fails(
    tmp_path: Path,
) -> None:
    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    make_database(source)
    environment = sqlite_cli_environment(tmp_path)
    failing_chmod = tmp_path / "chmod"
    failing_chmod.write_text("#!/usr/bin/env bash\nexit 1\n")
    failing_chmod.chmod(0o700)
    environment["PATH"] = f"{tmp_path}:{environment['PATH']}"

    result = run_restore(source, target, environment)

    assert result.returncode != 0
    assert not target.exists()
    assert not list(tmp_path.glob(".restore.*"))


def test_restore_leaves_no_files_when_publishing_fails(tmp_path: Path) -> None:
    source = tmp_path / "backup.db"
    target = tmp_path / "restored.db"
    make_database(source)
    environment = sqlite_cli_environment(tmp_path)
    failing_ln = tmp_path / "ln"
    failing_ln.write_text("#!/usr/bin/env bash\nexit 1\n")
    failing_ln.chmod(0o700)
    environment["PATH"] = f"{tmp_path}:{environment['PATH']}"

    result = run_restore(source, target, environment)

    assert result.returncode != 0
    assert not target.exists()
    assert not list(tmp_path.glob(".restore.*"))
