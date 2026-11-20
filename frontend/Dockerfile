# Built with the repository root as context (deploy/compose.yml), because the
# site's documentation pages are the Markdown files in docs/ (ADR 0020).

# Stage 1: build the static SvelteKit site.
FROM node:22-alpine AS build
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
COPY docs/ /src/docs/
RUN npm run build

# Stage 2: Caddy serves the build and proxies /api to the Django container.
FROM caddy:2-alpine
COPY --from=build /src/frontend/build /srv
