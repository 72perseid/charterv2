#!/bin/sh
# Restore a Chart-er backup set into the running compose stack.
#   deploy/restore.sh /root/backups/charter/2026-09-08T030000Z
# Stops the API and worker, replaces the database and the data volume, and
# starts them again. The env file in the set must match deploy/.env
# (same FERNET_KEY, or stored API keys become unreadable).
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
COMPOSE="docker compose -f $HERE/compose.yml"
SET=${1:?usage: restore.sh <backup set directory>}

test -f "$SET/charter.sql.gz" && test -f "$SET/data.tar.gz" || { echo "not a backup set: $SET"; exit 1; }

# Check both archives before touching anything.
gunzip -t "$SET/charter.sql.gz"
gunzip -t "$SET/data.tar.gz"

$COMPOSE stop api worker
trap '$COMPOSE start api worker' EXIT   # always bring the app back, even on failure

gunzip -c "$SET/charter.sql.gz" | $COMPOSE exec -T postgres psql -U charter -d charter -q -v ON_ERROR_STOP=1
gunzip -c "$SET/data.tar.gz" | $COMPOSE run --rm -T --no-deps --entrypoint sh api -c 'rm -rf /data/* && cd /data && tar xf -'
echo "restored from $SET"
