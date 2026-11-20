<script lang="ts">
  // The user guide, shortened (docs/guide/ is the long form). Readable without
  // signing in, so the landing page can link to it.
  import { t } from '$lib/i18n';
  import { session } from '$lib/session.svelte';
  import LanguageSwitch from '$lib/components/LanguageSwitch.svelte';

  const h = t.help;
</script>

<svelte:head><title>{h.title} · {t.appName}</title></svelte:head>

<!-- Signed in, AppShell already provides <main> and the language switch. -->
<svelte:element this={session.user ? 'div' : 'main'} class="help">
  {#if !session.user}
    <div class="top">
      <a href="/">{t.appName}</a>
      <LanguageSwitch />
    </div>
  {/if}

  <h1>{h.title}</h1>
  <p class="lead">{h.lead}</p>

  <nav aria-label={h.contents}>
    <h2>{h.contents}</h2>
    <ol>
      {#each h.sections as section (section.id)}
        <li><a href="#{section.id}">{section.title}</a></li>
      {/each}
    </ol>
  </nav>

  {#each h.sections as section, i (section.id)}
    <section id={section.id}>
      <h2>{section.title}</h2>
      {#each section.paragraphs as paragraph, j (j)}
        <p>{paragraph}</p>
      {/each}
      {#if section.points.length}
        <!-- The first section is a sequence of steps; the others are unordered. -->
        <svelte:element this={i === 0 ? 'ol' : 'ul'}>
          {#each section.points as point, j (j)}
            <li>{point}</li>
          {/each}
        </svelte:element>
      {/if}
    </section>
  {/each}
</svelte:element>

<style>
  .help {
    max-width: 44rem;
  }
  main.help {
    padding-top: 2rem;
  }
  .top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  .lead {
    font-size: 1.1rem;
    color: var(--ink-muted);
  }
  nav {
    border-left: 3px solid var(--primary);
    padding-left: 0.75rem;
    margin: 1.5rem 0 2rem;
  }
  nav h2 {
    font-size: 0.9rem;
    color: var(--ink-muted);
    font-weight: normal;
  }
  nav ol {
    margin: 0;
    padding-left: 1.25rem;
    columns: 2;
  }
  section {
    margin-bottom: 2rem;
    scroll-margin-top: 1rem;
  }
  section :global(ol),
  section :global(ul) {
    padding-left: 1.25rem;
  }
  section :global(li) {
    margin-bottom: 0.4rem;
  }
  @media (max-width: 36rem) {
    nav ol {
      columns: 1;
    }
  }
</style>
