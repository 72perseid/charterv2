# Running it with Docker

Chart-er is one compose file. If you have Docker with the Compose plugin, you have everything it needs: no Python, Node or database to install. The same file runs on a laptop and on a server.

## Start

```sh
git clone https://github.com/72perseid/charterv2.git chart-er && cd chart-er
cp deploy/.env.example deploy/.env        # then fill in the three secrets, see below
APP_VERSION=$(git rev-parse --short HEAD) docker compose -f deploy/compose.yml up --build -d
```

Open <http://localhost:8080> and create an account. The first build takes a few minutes; later ones take seconds unless dependencies changed.

Four containers start: PostgreSQL, the API, a worker that reads uploads and calls the model, and Caddy, which serves the site and passes `/api` on. Only Caddy publishes a port, on `127.0.0.1:8080`. The database and the uploaded files live in two Docker volumes.

To save typing in what follows:

```sh
alias dc='docker compose -f deploy/compose.yml'
```

## Settings

Everything is in `deploy/.env`. The file itself explains each line and how to generate the secrets.

| Variable | What it is |
|---|---|
| `SECRET_KEY` | Signs sessions. Changing it signs everyone out. |
| `POSTGRES_PASSWORD` | Set it before the first start. The database keeps the first value; changing it later locks the app out. |
| `FERNET_KEY` | Encrypts every user's model API key. **If it is lost or changed, the stored keys are unreadable** and each user has to enter theirs again. |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | The names the site is reached by. The defaults cover `localhost:8080`. |
| `CADDY_BIND` | Where the one port is published. Default `127.0.0.1:8080`. |
| `SECURE_COOKIES` | `true` once the site is served over https. |
| `ALLOW_PRIVATE_ENDPOINTS` | `true` lets users point at a model on this machine or network (Ollama, vLLM). Leave it `false` on a server strangers can register on. See the [README](../../README.md#running-with-a-local-model). |
| `EMAIL_URL`, `REQUIRE_EMAIL_VERIFICATION` | Optional. Without them registration is open to anyone who finds the site. |

After changing the file, `dc up -d` recreates the containers with the new values.

## On a server

Nothing changes: the same three commands, on any machine that runs Docker. A small VPS is enough; the four containers use well under 1 GB of memory. The reference installation runs this way.

What a public address adds:

- **HTTPS.** Either put the proxy you already have in front of `127.0.0.1:8080`, or let the compose Caddy do it: set a hostname in place of `:80` in `deploy/Caddyfile` and `CADDY_BIND` so that ports 80 and 443 are published. Caddy then gets the certificate itself.
- **The hostname** in `ALLOWED_HOSTS`, and `https://<hostname>` in `CSRF_TRUSTED_ORIGINS`. A missing entry shows as "Bad Request (400)" or "CSRF check failed".
- **`SECURE_COOKIES=true`.**
- **`ALLOW_PRIVATE_ENDPOINTS=false`**, so that a user cannot make the server call services on its own network.
- **Backups**, below.

## Is it running?

```sh
curl -s http://localhost:8080/api/health        # {"status": "ok", "version": "<commit>"}
dc ps
```

The health address needs no login. `version` is the commit the running image was built from, so it also tells you whether an update took effect. It does not cover the worker: if uploads stay *Pending*, look at `dc ps` and `dc logs worker`.

## Updating

```sh
git pull
APP_VERSION=$(git rev-parse --short HEAD) dc up --build -d
```

The API container applies database migrations when it starts. The site is away for a few seconds. Take a backup first.

## Backups

```sh
deploy/backup.sh                 # writes a dated set under /root/backups/charter
deploy/restore.sh <set>          # puts one back
```

A set holds a dump of the database, an archive of the uploaded files, and a copy of `deploy/.env`, because the database is useless for stored API keys without `FERNET_KEY`. Fourteen sets are kept. `BACKUP_DIR` changes the place, and `BACKUP_REMOTE` (an rsync target) copies every set to another machine. Backups that sit on the same disk as the data are lost with it.

For a nightly backup, a cron line on the host:

```
0 3 * * * /path/to/chart-er/deploy/backup.sh >> /var/log/charter-backup.log 2>&1
```

Restoring replaces the database and the files with the set's content; everything newer is gone. Try one restore before you rely on them. A set contains every user's data and the key to their API keys, so keep copies as private as the server.

## Looking inside

```sh
dc logs --tail 100 api           # requests, errors, migrations at start
dc logs -f worker                # one line per file read and per chart generated
dc exec api python manage.py createsuperuser      # a login for /admin
dc exec api python manage.py changepassword <email>
```

`/admin` lists users, datasets, charts and revisions. Deleting a user there removes their datasets and charts from the database but leaves their uploaded files in the data volume under `/data/<user id>/`.

Tests run in the same image: `dc run --rm api pytest`.

## When something is wrong

| Symptom | Look at |
|---|---|
| Nothing answers on the port | `dc ps`. A container that keeps restarting says why in `dc logs <name>`. |
| The page loads, every action says "Could not reach the server" | `dc logs api`. The API exits at start when a migration fails or a required variable is missing. |
| "Bad Request (400)" on every page | The hostname is not in `ALLOWED_HOSTS`. |
| Forms fail with "CSRF check failed" | The origin is not in `CSRF_TRUSTED_ORIGINS`, or `SECURE_COOKIES` does not match http/https. |
| Uploads stay *Pending*, charts stay *Waiting* | The worker: `dc logs worker`, `dc restart worker`. |
| One chart stays *Running* for ever | The worker was restarted in the middle of it. Make a new revision. |
| "Stored key cannot be decrypted with the current FERNET_KEY" | `FERNET_KEY` is not the one the keys were saved with. Put the old one back, from a backup set's `env`. |
| A local model cannot be reached | `ALLOW_PRIVATE_ENDPOINTS=true`, and the base URL `http://host.docker.internal:<port>/v1`: inside a container, `localhost` is the container. |

`dc restart api worker` is always safe. `dc down` stops everything and keeps the data. **`dc down -v` deletes the database and every uploaded file.**
