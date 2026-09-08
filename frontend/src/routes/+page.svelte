<script lang="ts">
  import { t } from '$lib/i18n/en';
  import { session } from '$lib/session.svelte';
</script>

<svelte:head><title>{t.appName}</title></svelte:head>

<main class="landing">
  <h1>{t.landing.title}</h1>
  <p class="lead">{t.landing.lead}</p>
  <ol>
    {#each t.landing.what as line, i (i)}
      <li>{line}</li>
    {/each}
  </ol>
  <p class="flow">{t.landing.dataFlow}</p>
  <p class="actions">
    {#if session.user}
      <a class="button" href="/datasets">{t.nav.datasets}</a>
    {:else}
      <a class="button" href="/login">{t.landing.signIn}</a>
      <a class="button quiet" href="/register">{t.landing.register}</a>
    {/if}
  </p>
</main>

<style>
  .landing {
    max-width: 40rem;
    padding-top: 4rem;
  }
  .lead {
    font-size: 1.15rem;
  }
  ol {
    padding-left: 1.25rem;
  }
  li {
    margin-bottom: 0.5rem;
  }
  .flow {
    font-size: 0.9rem;
    color: var(--ink-muted);
    border-left: 3px solid var(--primary);
    padding-left: 0.75rem;
  }
  .actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 2rem;
  }
</style>
