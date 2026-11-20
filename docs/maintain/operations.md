# Operations

Keeping the installation healthy: backups, looking at what it is doing, accounts, and what to check when it misbehaves. Commands run on the server in `/root/chart-er` unless they start with `ssh` or `curl`. To save typing:

```sh
alias dc='docker compose -f /root/chart-er/deploy/compose.yml'
```

## Is it up?

```sh
curl -s https://charter.tugcekoseoglu.com/api/health
```

`{"status": "ok", "version": "…"}` means the proxy chain, the API and the database all answer, and tells you which commit is running. It needs no login, so an uptime monitor can watch it. A 503 with `database unavailable` means the API runs and PostgreSQL does not.

The health check does not cover the worker. If uploads stay *Pending*, the worker is down: `dc ps`.

## Backups

`deploy/backup.sh` writes one dated directory per run under `/root/backups/charter/`:

| File | Content |
|---|---|
| `charter.sql.gz` | the whole database |
| `data.tar.gz` | every uploaded file and its parsed copy |
| `env` | a copy of `deploy/.env`, because the database is useless for stored API keys without `FERNET_KEY` |

It keeps the newest fourteen sets. It should run every night from root's crontab:

```
0 3 * * * /root/chart-er/deploy/backup.sh >> /var/log/charter-backup.log 2>&1
```

Check that it does: `crontab -l`, and `ls /root/backups/charter | tail -3` should end with last night's date.

Run it by hand before every deploy and before anything else you are unsure of. It takes seconds and does not interrupt the site.

**Backups are on the same machine as the data.** If the server is lost, so are they. Set `BACKUP_REMOTE` to an rsync target on another machine (`user@host:/backups/charter`) in the cron line's environment and the script syncs every set there. Until that is done, copy a set to your own computer from time to time:

```sh
rsync -a root@<server>:/root/backups/charter/<set> ~/charter-backups/
```

A backup set contains every user's data and the key that decrypts their API keys. Store copies as carefully as the server itself.

### Restore

```sh
/root/chart-er/deploy/restore.sh /root/backups/charter/2026-11-19T212207Z
```

The script checks both archives, stops the API and the worker, replaces the database and the files, and starts them again even if a step fails. Everything created after that backup is gone, so take a fresh backup first unless the current state is the problem.

`deploy/.env` must hold the same `FERNET_KEY` as the `env` file in the set. On a new server, use the set's `env` as `deploy/.env`.

A backup that has never been restored is a hope, not a backup. Do one test restore before relying on them, for example before the conference: on a second machine, or on the server at a quiet moment directly after a fresh backup.

## Logs

```sh
dc logs --tail 100 api        # requests, errors, migrations at start
dc logs --tail 100 worker     # one line per dataset parsed and per revision generated
dc logs -f worker             # follow
```

Every revision writes one line with the revision id, user id, endpoint host, model, duration, tokens and outcome. The request and the answer themselves are not in the log; they are in the database with the revision.

## Accounts and data

`/admin` (sign in with a superuser) lists users, datasets, charts and revisions.

| Task | How |
|---|---|
| Create an admin | `dc exec api python manage.py createsuperuser` |
| Reset a password | `dc exec api python manage.py changepassword <email>` |
| Lock an account | in `/admin`, untick *Active* on the user |
| Delete an account | in `/admin`, delete the user: their datasets, charts and stored key go with it. The uploaded files under `/data/<user id>/` stay on disk; remove that directory too. |
| Count users | `dc exec api python manage.py shell -c "from accounts.models import User; print(User.objects.count())"` |

Registration is open: anyone who finds the site can create an account. Each account costs disk space only, since every user brings their own model key, and uploads are limited per hour. If that becomes a problem, set `EMAIL_URL` and `REQUIRE_EMAIL_VERIFICATION=true` (SPEC §9).

Users' API keys are stored encrypted, but the server can decrypt them. Do not print, log or copy them.

## Disk

```sh
df -h /
docker system df
du -sh /root/backups/charter
```

Old images pile up with every deploy. `docker image prune -f` removes the unused ones. **Never run `docker system prune --volumes` or `docker volume prune` on this machine**: the volumes are the data, Chart-er's and the other stacks'.

## When something is wrong

Work from the outside in.

| Symptom | Check |
|---|---|
| The site does not load at all | `curl -I https://charter.tugcekoseoglu.com`. A certificate or connection error is the host Caddy: `systemctl status caddy`, `journalctl -u caddy -n 50`. A 502 means Caddy runs and nothing answers on 8080: `dc ps`. |
| The page loads, everything says "Could not reach the server" | `dc ps`, then `dc logs --tail 50 api`. The `api` container exits at start when a migration fails or a required variable is missing from `.env`. |
| Sign-in or any form fails with "CSRF check failed" | The hostname in the browser is not in `CSRF_TRUSTED_ORIGINS` as `https://…`, or `SECURE_COOKIES` does not match http/https. |
| "Bad Request (400)" on every page | The hostname is not in `ALLOWED_HOSTS`. |
| Uploads stay *Pending*, charts stay *Waiting* | The worker: `dc ps`, `dc logs --tail 50 worker`, `dc restart worker`. |
| One revision stays *Running* for ever | The worker was restarted in the middle of it. Nothing retries it; the user makes a new revision. |
| Every chart fails for one user | Their model or key, not the server. The reason is on their chart page. |
| Every chart fails for everyone | The server cannot reach the internet, or the worker's image is broken: `dc logs worker`. |
| "Stored key cannot be decrypted with the current FERNET_KEY" | `FERNET_KEY` in `.env` is not the one the keys were encrypted with. Put the old one back from a backup set's `env`. |

`dc restart api worker` is always safe. `dc down` stops the site but keeps the data; `dc down -v` **deletes the database and every file**. There is no reason to type it on the server.

## Routine

- **Before each deploy:** backup, CI green, health check afterwards.
- **Monthly:** `ls /root/backups/charter | tail`, `df -h /`, copy one backup set off the machine, `docker image prune -f`.
- **Yearly, or before an event:** a test restore; `apt upgrade` on the host; review whether registration should stay open.
- **Dependencies:** the ranges in `backend/pyproject.toml` pick up bug-fix releases at every image build. Django 5.2 is supported until April 2028; plan the move to the next LTS before then.
