<script lang="ts">
  import { doc, sections } from '$lib/docs';
  import { language, t } from '$lib/i18n';
</script>

<svelte:head><title>{t.docs.title} · {t.appName}</title></svelte:head>

<h1>{t.docs.title}</h1>
<p class="lead">{t.docs.lead}</p>

{#each sections as section (section.id)}
  <section>
    <h2>{t.docs.sections[section.id]}</h2>
    <p>{t.docs.sectionLead[section.id]}</p>
    <ol>
      {#each section.pages as p (p)}
        <li><a href="/docs/{section.id}/{p}">{doc(section.id, p, language).title}</a></li>
      {/each}
    </ol>
  </section>
{/each}

<style>
  .lead {
    font-size: 1.1rem;
    color: var(--ink-muted);
  }
  section {
    margin-top: 2rem;
  }
  ol {
    padding-left: 1.25rem;
  }
  li {
    margin-bottom: 0.3rem;
  }
</style>
