#!/bin/sh
# Nightly backup for Chart-er (SPEC §9): a pg_dump of the database and a tar
# of the data volume, kept locally with rotation, and optionally pushed
# off-box with rsync. Run from cron on the host; see README "Backups".
#
#   0 3 * * * /root/chart-er/deploy/backup.sh >> /var/log/charter-backup.log 2>&1
#
# Environment (optional):
#   BACKUP_DIR      where to keep local copies       (default /root/backups/charter)
#   BACKUP_KEEP     how many nightly sets to keep     (default 14)
#   BACKUP_REMOTE   rsync target, e.g. user@host:/backups/charter  (default: none)
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
COMPOSE="docker compose -f $HERE/compose.yml"
BACKUP_DIR=${BACKUP_DIR:-/root/backups/charter}
BACKUP_KEEP=${BACKUP_KEEP:-14}
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
TARGET="$BACKUP_DIR/$STAMP"

mkdir -p "$TARGET"
echo "[$STAMP] backup to $TARGET"

# 1. Database: a plain-SQL dump, compressed. Restore with psql (see README).
$COMPOSE exec -T postgres pg_dump -U charter --clean --if-exists charter | gzip > "$TARGET/charter.sql.gz"

# 2. Files: the data volume (originals and parsed parquet), as a tarball.
$COMPOSE run --rm -T --no-deps --entrypoint sh api -c 'cd /data && tar cf - .' | gzip > "$TARGET/data.tar.gz"

# 3. The env file, so a restore has the same SECRET_KEY and FERNET_KEY.
#    Keys stored in the database are unreadable without FERNET_KEY.
cp "$HERE/.env" "$TARGET/env"
chmod 600 "$TARGET/env"

du -sh "$TARGET"/* | sed 's/^/  /'

# 4. Rotation.
ls -1d "$BACKUP_DIR"/*/ 2>/dev/null | sort | head -n -"$BACKUP_KEEP" | xargs -r rm -rf

# 5. Off-box copy, if configured.
if [ -n "${BACKUP_REMOTE:-}" ]; then
  rsync -az --delete "$BACKUP_DIR/" "$BACKUP_REMOTE/"
  echo "  synced to $BACKUP_REMOTE"
fi
echo "[$STAMP] done"
