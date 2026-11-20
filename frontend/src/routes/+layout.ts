import { auth, ApiError } from '$lib/api';
import { session } from '$lib/session.svelte';
import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

// Client-rendered SPA behind Caddy (SPEC §8). No server-side rendering.
export const ssr = false;
export const prerender = false;

const PUBLIC = new Set(['/', '/login', '/register', '/help']);

export const load: LayoutLoad = async ({ url }) => {
  if (session.user === null) {
    try {
      session.set(await auth.me());
    } catch (e) {
      if (!(e instanceof ApiError && e.status === 401)) throw e;
    }
  }
  const signedIn = session.user !== null;
  if (!signedIn && !PUBLIC.has(url.pathname)) {
    redirect(302, '/login?next=' + encodeURIComponent(url.pathname));
  }
  if (signedIn && (url.pathname === '/login' || url.pathname === '/register')) {
    redirect(302, '/datasets');
  }
  return {};
};
