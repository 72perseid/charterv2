<script lang="ts">
  // The documentation section: a list of pages beside the page. The pages are
  // the Markdown files of docs/ (src/lib/docs.ts). Readable without signing in.
  import { afterNavigate } from '$app/navigation';
  import { page } from '$app/state';
  import { doc, sections } from '$lib/docs';
  import { language, t } from '$lib/i18n';
  import { session } from '$lib/session.svelte';
  import LanguageSwitch from '$lib/components/LanguageSwitch.svelte';

  let { children } = $props();

  // On a phone the list of pages is folded away above the page, and folds again after a choice.
  const wide = typeof matchMedia === 'undefined' || matchMedia('(min-width: 48rem)').matches;
  let unfolded = $state(wide);
  afterNavigate(() => {
    if (!wide) unfolded = false;
  });

  const groups = sections.map((s) => ({
    id: s.id,
    label: t.docs.sections[s.id],
    pages: s.pages.map((p) => ({ href: `/docs/${s.id}/${p}`, title: doc(s.id, p, language).title }))
  }));
</script>

<!-- Signed in, AppShell already provides <main> and the language switch. -->
<svelte:element this={session.user ? 'div' : 'main'}>
  {#if !session.user}
    <div class="top">
      <a href="/">{t.appName}</a>
      <LanguageSwitch />
    </div>
  {/if}

  <div class="docs">
    <nav aria-label={t.docs.contents}>
      <details bind:open={unfolded}>
      <summary>{t.docs.contents}</summary>
      <a class="home" href="/docs" aria-current={page.url.pathname === '/docs' ? 'page' : undefined}>
        {t.docs.title}
      </a>
      {#each groups as group (group.id)}
        <h2>{group.label}</h2>
        <ul>
          {#each group.pages as p (p.href)}
            <li><a href={p.href} aria-current={page.url.pathname === p.href ? 'page' : undefined}>{p.title}</a></li>
          {/each}
        </ul>
      {/each}
      </details>
    </nav>
    <div class="body">
      {@render children()}
    </div>
  </div>
</svelte:element>

<style>
  .top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  .docs {
    display: grid;
    grid-template-columns: 14rem minmax(0, 1fr);
    gap: 2.5rem;
    align-items: start;
  }
  nav {
    position: sticky;
    top: 1rem;
    font-size: 0.9rem;
  }
  summary {
    display: none;
  }
  nav h2 {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--ink-muted);
    margin: 1.25rem 0 0.35rem;
  }
  nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  nav a {
    display: block;
    padding: 0.2rem 0.6rem;
    border-left: 2px solid var(--line);
    color: var(--ink);
    text-decoration: none;
  }
  nav a:hover {
    border-left-color: var(--ink-muted);
  }
  nav a[aria-current='page'] {
    border-left-color: var(--primary);
    color: var(--primary-ink);
    font-weight: 600;
  }
  nav a.home {
    border-left: 0;
    padding-left: 0;
    font-weight: 600;
  }
  .body {
    max-width: 44rem;
  }
  @media (max-width: 48rem) {
    .docs {
      grid-template-columns: minmax(0, 1fr);
      gap: 1.5rem;
    }
    nav {
      position: static;
      border-bottom: 1px solid var(--line);
      padding-bottom: 0.75rem;
    }
    summary {
      display: list-item;
      cursor: pointer;
      font-weight: 600;
    }
    details[open] summary {
      margin-bottom: 0.75rem;
    }
  }
</style>
