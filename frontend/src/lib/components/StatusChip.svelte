<script lang="ts">
  import { t } from '$lib/i18n/en';

  let { status }: { status: 'pending' | 'running' | 'done' | 'failed' } = $props();
</script>

<span class="chip {status}">
  {#if status === 'running'}<span class="dot" aria-hidden="true"></span>{/if}
  {t.status[status]}
</span>

<style>
  .chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: var(--ground);
  }
  .done {
    border-color: var(--success);
    color: var(--success);
  }
  .failed {
    border-color: var(--destructive);
    color: var(--destructive);
  }
  .running {
    border-color: var(--warning);
    color: var(--warning);
  }
  /* A visible running state is a spec requirement (SPEC §8). */
  .dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    background: currentColor;
    animation: pulse 1.2s ease-in-out infinite;
  }
  @keyframes pulse {
    50% {
      opacity: 0.3;
    }
  }
</style>
