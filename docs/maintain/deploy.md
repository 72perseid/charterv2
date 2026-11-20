# Deployment

How the reference installation at <https://charter.tugcekoseoglu.com> is set up, and how a new version gets there. `<server>` stands for the server's address throughout; SSH is key-based, as root.

## What is on the server

A rented VPS (Contabo, EU; Ubuntu 24.04, 4 vCPU, 7.8 GB RAM) that also runs other, unrelated stacks. **Chart-er shares the machine with them and nothing else**: not a database, not a network, not a volume.

| What | Where |
|---|---|
| The code | `/root/chart-er`, a plain copy of the repository. **Not a git checkout.** |
| Configuration and secrets | `/root/chart-er/deploy/.env`. Not in git, not overwritten by a deploy. |
| Containers | compose project `charter`: `postgres`, `api`, `worker`, `caddy` |
| Data | Docker volumes `charter_pgdata` (database) and `charter_data` (uploaded files) |
| Published port | `127.0.0.1:8080` only, the compose Caddy |
| TLS and the hostname | the host's own Caddy, `/etc/caddy/Caddyfile`, shared with the other stacks |
| Backups | `/root/backups/charter/<timestamp>/` |

The request path is: browser → host Caddy (443, certificate) → `localhost:8080` → compose Caddy → static files, or the `api` container.

## Deploying a version

From the repository on your own machine, on `main`, with CI green for the commit.

```sh
SHA=$(git rev-parse --short HEAD)

# 1. Back up first. Takes a few seconds; see operations.md.
ssh root@<server> /root/chart-er/deploy/backup.sh

# 2. Copy the committed tree. Uncommitted changes are not sent, deploy/.env is not touched.
git archive --format=tar HEAD | ssh root@<server> 'tar -x -C /root/chart-er --no-same-owner'

# 3. Build and restart. Only Chart-er's containers are affected.
ssh root@<server> "cd /root/chart-er && APP_VERSION=$SHA docker compose -f deploy/compose.yml up --build -d"

# 4. Check.
curl -s https://charter.tugcekoseoglu.com/api/health      # {"status": "ok", "version": "<SHA>"}
```

What happens in step 3: the images are rebuilt (two to four minutes when dependencies changed, seconds otherwise), the `api` container runs pending migrations and starts, the worker restarts. The site is unavailable for a few seconds. A chart that was being generated at that moment stays *Running*; ask its owner to revise it again.

`git archive` only adds and overwrites. A file deleted from the repository stays on the server; it is harmless unless it is a migration or a module that something still imports. Remove such a file by hand.

**The health check is the proof of a deploy.** `version` is the commit the running image was built from. If it shows the old commit, the build failed: read the output of step 3. If it does not answer, see [Operations](operations.md#when-something-is-wrong).

After the health check, sign in once and open a chart. That exercises the database, the files and the frontend build together.

## Going back

Deploy the previous commit the same way, from a checkout of it:

```sh
git archive --format=tar <old-sha> | ssh root@<server> 'tar -x -C /root/chart-er --no-same-owner'
ssh root@<server> "cd /root/chart-er && APP_VERSION=<old-sha> docker compose -f deploy/compose.yml up --build -d"
```

This is safe when the newer version added no migration. If it did, the old code meets a newer database: usually harmless for an added column, but if in doubt restore the backup from step 1 as well ([Operations](operations.md#restore)).

## Configuration

`deploy/.env` on the server. `deploy/.env.example` documents every variable. The ones that matter here:

| Variable | Value on the server | Note |
|---|---|---|
| `SECRET_KEY`, `POSTGRES_PASSWORD` | secrets | Changing `SECRET_KEY` signs everyone out. Do not change `POSTGRES_PASSWORD` after the first start: the database keeps the old one. |
| `FERNET_KEY` | secret | **Encrypts every user's API key. If it is lost or changed, all stored keys are unreadable** and each user must enter theirs again. It is copied into every backup set. |
| `ALLOWED_HOSTS` | both hostnames | Django answers only for these. |
| `CSRF_TRUSTED_ORIGINS` | `https://` + both hostnames | Without the right origin, every form submission fails with "CSRF check failed". |
| `SECURE_COOKIES` | `true` | Because the public origin is https. |
| `ALLOW_PRIVATE_ENDPOINTS` | `false` | Must stay false on a public server: it stops a user from making the server call services on its own network (ADR 0016). |
| `EMAIL_URL`, `REQUIRE_EMAIL_VERIFICATION` | unset | Registration is open. |

After editing `.env`: `docker compose -f deploy/compose.yml up -d` recreates the containers with the new values. Keep a dated copy of the file before editing it.

## The hostname

Two blocks in the host's `/etc/caddy/Caddyfile`:

```
charter.tugcekoseoglu.com {
    reverse_proxy localhost:8080
}

charter.72perseids.com {
    redir https://charter.tugcekoseoglu.com{uri} permanent
}
```

To move to another name:

1. Add a DNS A record for the new name pointing at the server, and wait until `dig +short <name>` shows it.
2. Add the name to `ALLOWED_HOSTS` and `https://<name>` to `CSRF_TRUSTED_ORIGINS` in `deploy/.env`; recreate the containers.
3. Copy the Caddyfile to a dated backup, add a block for the new name, run `caddy validate --config /etc/caddy/Caddyfile`, then `systemctl reload caddy`. **Reload, not restart**: the other sites on the machine stay up. Caddy fetches the certificate by itself within a minute.
4. Check `https://<name>/api/health`, then turn the old block into a redirect.
5. Update SPEC §9 and §14.

The Caddyfile belongs to every stack on the machine. Change only Chart-er's blocks.

## Setting up a new server

1. Install Docker with the Compose plugin.
2. Copy the repository to the server (`git archive` as above, into an empty directory).
3. `cp deploy/.env.example deploy/.env` and fill in the three secrets, the hostnames, and `SECURE_COOKIES=true`.
4. Start it as in step 3 of a deploy.
5. Put a TLS proxy in front of `127.0.0.1:8080`, or set `CADDY_BIND` and a hostname in `deploy/Caddyfile` and let the compose Caddy hold ports 80 and 443 itself.
6. `docker compose -f deploy/compose.yml exec api python manage.py createsuperuser` for `/admin`.
7. Install the backup cron line ([Operations](operations.md#backups)) and do one restore as a test.

To move an existing installation, restore its latest backup set on the new server after step 4, using the `env` file from the set as `deploy/.env`.
