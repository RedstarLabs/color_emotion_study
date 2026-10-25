#!/usr/bin/env bash
set -euo pipefail

database_path="${DATABASE_PATH:?Set DATABASE_PATH to the absolute SQLite file}"
backup_directory="${BACKUP_DIRECTORY:?Set BACKUP_DIRECTORY to a private directory}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
destination="${backup_directory}/coloremotionstudy-${timestamp}.db"

test -f "$database_path"
test ! -L "$database_path"
if [[ -e "$backup_directory" || -L "$backup_directory" ]]; then
    test -d "$backup_directory"
    test ! -L "$backup_directory"
fi
install -d -m 700 "$backup_directory"
chmod 700 "$backup_directory"
umask 077
sqlite3 "$database_path" ".backup '$destination'"
chmod 600 "$destination"
printf 'Created backup: %s\n' "$destination"
