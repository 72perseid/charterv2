<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { auth, type User } from '$lib/api';
  import { session } from '$lib/session.svelte';
  import { t } from '$lib/i18n/en';
  import type { Snippet } from 'svelte';

  let { user, children }: { user: User; children: Snippet } = $props();

  // One nav definition for the whole app (SPEC §13).
  const links = [
    { href: '/datasets', label: t.nav.datasets },
    { href: '/charts', label: t.nav.charts },
    { href: '/settings', label: t.nav.settings }
  ];

  function isCurrent(href: string): boolean {
    return page.url.pathname === href || page.url.pathname.startsWith(href + '/');
  }

  async function signOut() {
    await auth.logout();
    session.set(null);
    await goto('/login');
  }
</script>

<header class="shell-header">
  <div class="inner">
    <a class="brand" href="/datasets">{t.appName}</a>
    <nav>
      {#each links as link (link.href)}
        <a href={link.href} aria-current={isCurrent(link.href) ? 'page' : undefined}>{link.label}</a>
      {/each}
    </nav>
    <span class="spacer"></span>
    <span class="who">{user.display_name || user.email}</span>
    <button class="quiet" type="button" onclick={signOut}>{t.nav.signOut}</button>
  </div>
</header>

<main>
  {@render children()}
</main>
