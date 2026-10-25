#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: restore.sh BACKUP_DB TARGET_DB" >&2
    exit 2
}

[[ $# -eq 2 ]] || usage
source_database="$1"
target_database="$2"

case "$source_database$target_database" in
    *"'"*) echo "Paths must not contain single quotes" >&2; exit 2 ;;
esac

case "$source_database" in
    /*) ;;
    *) echo "BACKUP_DB must be an absolute path" >&2; exit 2 ;;
esac
case "$target_database" in
    /*) ;;
    *) echo "TARGET_DB must be an absolute path" >&2; exit 2 ;;
esac

[[ -f "$source_database" && ! -L "$source_database" ]] || {
    echo "BACKUP_DB must be an existing regular file, not a symlink" >&2
    exit 2
}

target_directory="$(dirname "$target_database")"
[[ -d "$target_directory" ]] || {
    echo "Target directory does not exist: $target_directory" >&2
    exit 2
}

source_realpath="$(realpath -- "$source_database")"
target_realpath="$(realpath -m -- "$target_database")"
if [[ "$source_realpath" == "$target_realpath" ]]; then
    echo "BACKUP_DB and TARGET_DB must be different files" >&2
    exit 2
fi

if [[ -e "$target_database" || -L "$target_database" ]]; then
    echo "TARGET_DB already exists; refusing to overwrite: $target_database" >&2
    exit 2
fi

integrity_output="$(sqlite3 -batch "$source_database" "PRAGMA integrity_check;" 2>/dev/null)" || {
    echo "BACKUP_DB could not be checked" >&2
    exit 1
}
if [[ "$integrity_output" != "ok" ]]; then
    echo "BACKUP_DB failed integrity_check" >&2
    exit 1
fi

umask 077
temporary_database="$(mktemp "$target_directory/.restore.XXXXXXXX")"
cleanup() {
    rm -f -- "$temporary_database"
}
trap cleanup EXIT

if ! sqlite3 "$source_database" ".backup '$temporary_database'" 2>/dev/null; then
    echo "Database restore failed" >&2
    exit 1
fi

temporary_integrity="$(sqlite3 -batch "$temporary_database" "PRAGMA integrity_check;" 2>/dev/null)" || {
    echo "Restored database failed integrity_check" >&2
    exit 1
}
if [[ "$temporary_integrity" != "ok" ]]; then
    echo "Restored database failed integrity_check" >&2
    exit 1
fi

if ! chmod 600 -- "$temporary_database"; then
    echo "Could not set restored database permissions" >&2
    exit 1
fi
if [[ "$(stat -c '%a' -- "$temporary_database")" != "600" ]]; then
    echo "Restored database permissions are not 0600" >&2
    exit 1
fi

# ln(1) fails atomically if another process creates the target first.
if ! ln -- "$temporary_database" "$target_database"; then
    echo "TARGET_DB was created concurrently; refusing to overwrite" >&2
    exit 1
fi
printf 'Restored test/target database: %s\n' "$target_database"
