import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    // Local development against a running API; production uses Caddy instead.
    proxy: { '/api': 'http://127.0.0.1:8000' }
  },
  test: { include: ['src/**/*.test.ts'] }
});
