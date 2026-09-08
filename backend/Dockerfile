FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Dependencies first so source edits do not invalidate the layer.
COPY pyproject.toml ./
RUN mkdir -p charter accounts datasets generation && pip install --no-cache-dir ".[dev]"

COPY . .
# Admin static files are served by Caddy from a shared volume (see deploy/compose.yml).
RUN SECRET_KEY=build DATABASE_URL=postgres://x:x@x/x python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn charter.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"]
