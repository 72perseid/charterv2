# ADR 0009: SvelteKit with the static adapter and hand-written CSS

Date: 2026-09-08. Status: accepted.

Small, readable, and not the generated-app default. Static output means one fewer server process; Caddy serves the files and proxies `/api`. Vite is present only as SvelteKit's build tool. No component library, no Tailwind, no client-side cache library, no i18n library: strings live in one file per language and the language switch reloads the page.

Rejected: React + Vite + shadcn, the v1 stack, recognisable as generated code; Angular, heavier than the problem.
