import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Single-page build: every route is served index.html and rendered in the browser.
    // Caddy serves the build directory and proxies /api (see deploy/Caddyfile).
    adapter: adapter({ fallback: 'index.html', strict: false })
  }
};

export default config;
