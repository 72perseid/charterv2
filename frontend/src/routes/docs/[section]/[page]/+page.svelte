<script lang="ts">
  import { directory, doc, render, sections } from '$lib/docs';
  import { language, t } from '$lib/i18n';

  let { data } = $props();

  const d = $derived(doc(data.section, data.page, language));
  // The Markdown is this repository's own text, built into the site; nothing a user typed.
  const html = $derived(render(d.text, directory(d, language)));

  const order = sections.flatMap((s) => s.pages.map((p) => ({ section: s.id, page: p })));
  const at = $derived(order.findIndex((o) => o.section === data.section && o.page === data.page));
  const previous = $derived(at > 0 ? order[at - 1] : null);
  const next = $derived(at < order.length - 1 ? order[at + 1] : null);
</script>

<svelte:head><title>{d.title} · {t.appName}</title></svelte:head>

{#if !d.translated}
  <p class="note" lang={language}>{t.docs.englishOnly}</p>
{/if}

<article class="doc" lang={d.translated ? language : 'en'}>
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html html}
</article>

<nav class="turn" aria-label={t.docs.contents}>
  {#if previous}
    <a href="/docs/{previous.section}/{previous.page}">
      <span>{t.docs.previous}</span>
      {doc(previous.section, previous.page, language).title}
    </a>
  {:else}
    <span></span>
  {/if}
  {#if next}
    <a class="next" href="/docs/{next.section}/{next.page}">
      <span>{t.docs.next}</span>
      {doc(next.section, next.page, language).title}
    </a>
  {/if}
</nav>

<style>
  .note {
    font-size: 0.9rem;
    color: var(--ink-muted);
    border-left: 3px solid var(--warning);
    padding-left: 0.75rem;
  }
  .doc :global(h1) {
    margin-bottom: 1rem;
  }
  .doc :global(h2) {
    margin-top: 2.25rem;
    padding-top: 0.25rem;
    scroll-margin-top: 1rem;
  }
  .doc :global(h3) {
    font-size: 1rem;
    margin-top: 1.5rem;
    scroll-margin-top: 1rem;
  }
  .doc :global(ul),
  .doc :global(ol) {
    padding-left: 1.25rem;
    margin: 0 0 1rem;
  }
  .doc :global(li) {
    margin-bottom: 0.35rem;
  }
  .doc :global(li > p) {
    margin-bottom: 0.35rem;
  }
  .doc :global(code) {
    font-family: var(--font-mono);
    font-size: 0.875em;
    background: var(--accent);
    padding: 0.05rem 0.3rem;
    border-radius: 0.25rem;
    overflow-wrap: anywhere;
  }
  .doc :global(pre) {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    overflow-x: auto;
    line-height: 1.4;
    margin: 0 0 1rem;
  }
  .doc :global(pre code) {
    background: none;
    padding: 0;
    font-size: 0.82rem;
    overflow-wrap: normal;
  }
  .doc :global(blockquote) {
    margin: 0 0 1rem;
    padding-left: 0.75rem;
    border-left: 3px solid var(--primary);
    color: var(--ink-muted);
  }
  .doc :global(.table) {
    overflow-x: auto;
    margin: 0 0 1rem;
  }
  .doc :global(table) {
    width: 100%;
    font-size: 0.92rem;
  }
  .doc :global(th),
  .doc :global(td) {
    vertical-align: top;
    white-space: normal;
  }
  /* A table whose header row is empty is a list of pairs, not a grid. */
  .doc :global(thead:not(:has(th:not(:empty)))) {
    display: none;
  }
  .turn {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
  }
  .turn a {
    text-decoration: none;
    font-weight: 600;
  }
  .turn a span {
    display: block;
    font-size: 0.8rem;
    font-weight: normal;
    color: var(--ink-muted);
  }
  .turn .next {
    text-align: right;
  }
</style>
