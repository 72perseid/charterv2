<script lang="ts">
  import { language, languages, setLanguage, t } from '$lib/i18n';
</script>

<span class="lang" role="group" aria-label={t.language.label}>
  {#each languages as l, i (l)}
    {#if i > 0}<span aria-hidden="true">·</span>{/if}
    <button type="button" class:active={l === language} onclick={() => l !== language && setLanguage(l)} lang={l}>
      {l.toUpperCase()}
    </button>
  {/each}
</span>

<style>
  .lang {
    display: inline-flex;
    gap: 0.35rem;
    align-items: center;
    font-size: 0.8rem;
    color: var(--ink-muted);
  }
  button {
    background: none;
    border: 0;
    padding: 0.1rem 0.2rem;
    color: inherit;
    font-size: inherit;
  }
  button.active {
    color: var(--ink);
    font-weight: 600;
  }
</style>
