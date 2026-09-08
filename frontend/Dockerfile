# Stage 1: build the static SvelteKit site.
FROM node:22-alpine AS build
WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Caddy serves the build and proxies /api to the Django container.
FROM caddy:2-alpine
COPY --from=build /src/build /srv
