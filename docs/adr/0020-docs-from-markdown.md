# ADR 0020: The site's documentation is the repository's Markdown, rendered with marked

Date: 2026-11-20. Status: accepted.

Chart-er had its documentation in two places for one evening: a user guide and maintainer pages as Markdown under `docs/`, and a shortened help page in the app whose text lived in the i18n files. The repository was private, so the people the guide was written for could not read it, and the short page was already a second text to keep in step with the first.

**Decision.** The site serves the documentation itself under `/docs`, and it serves the files of `docs/guide/` and `docs/maintain/`, not a copy. `frontend/src/lib/docs.ts` reads them at build time with Vite's `import.meta.glob(…, { query: '?raw' })` and renders them in the browser. The short help page is removed; `/help` redirects.

- **One text.** What GitHub shows under `docs/` is what the site shows. Links are written relative, as GitHub needs them; on the site, links between these pages become routes, and links to the rest of the repository (README, SPEC, ADRs) go to GitHub. Heading anchors are made the way GitHub makes them, so one link works in both places.
- **Turkish.** A file of the same name in a `tr/` folder beside the English one is the translation, shown when the interface is in Turkish. The user guide is translated, since its readers are the archaeologists the tool is for. The maintainer pages are not: their reader works in a terminal in English. A page without a translation says so and shows the English text.
- **Public.** `/docs` needs no account, like the landing page, so someone can read how the thing works before trusting it with a file.

**The dependency: `marked`.** Rendering Markdown needs a parser. `marked` has no dependencies of its own, is about 40 kB in the documentation route's chunk only, and supports the tables and fenced code the pages use. Rejected:

- *Writing a parser.* Tables, nested lists and inline code inside links are exactly where a hand-written one goes wrong, and nobody should have to maintain it.
- *mdsvex.* It turns Markdown into Svelte components at compile time, which is more machinery than eleven pages need, and its link and heading handling would still have to be customised.
- *A separate documentation site* (MkDocs, Docusaurus). A second build, a second deploy and a second design for something that is part of the product.
- *Converting to HTML in the backend image.* The frontend is a static build; the pages belong in it.

The HTML goes in with `{@html}`. That is acceptable only because the input is the repository's own files, fixed at build time. Nothing a user types is ever rendered this way, and it must stay so.

**Consequence for the build.** The frontend image is now built with the repository root as its context (`deploy/compose.yml`, `frontend/Dockerfile`), because `docs/` is outside `frontend/`. A root `.dockerignore` keeps the context small. `vite.config.ts` allows the dev server to read one directory up.

**What this does not do.** The SPEC, the architecture page and the ADRs are not on the site; they are for readers of the code and stay on GitHub. There is no search; eleven pages have a menu. The two languages are kept in step by hand: the tests check that every listed page exists in English and that no link on the site is dead, not that a translation is current.
