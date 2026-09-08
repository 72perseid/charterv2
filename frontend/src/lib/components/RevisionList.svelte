<script lang="ts">
  import type { RevisionSummary } from '$lib/api';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import { t } from '$lib/i18n';

  let {
    chartId,
    revisions,
    selectedId,
    currentId
  }: {
    chartId: number;
    revisions: RevisionSummary[];
    selectedId: number | null;
    currentId: number | null;
  } = $props();

  const s = t.charts.page;
  const money = (usd: number) => '$' + (usd < 0.01 ? usd.toFixed(5) : usd.toFixed(3));
</script>

<nav class="revisions" aria-label={s.revisions}>
  <h2>{s.revisions}</h2>
  <ol>
    {#each [...revisions].reverse() as r (r.id)}
      <li class:selected={r.id === selectedId}>
        <a href="/charts/{chartId}?revision={r.id}">
          <span class="head">
            <span class="no">{s.revision} {r.revision_no}</span>
            <StatusChip status={r.status} />
            {#if r.id === currentId}<span class="current">{s.current}</span>{/if}
          </span>
          <span class="prompt">{r.prompt}</span>
          <span class="meta">
            {r.x_field} × {r.y_field}{#if r.color_field} · {r.color_field}{/if}
            {#if r.model} · {r.model}{/if}
            {#if r.duration_ms !== null} · {(r.duration_ms / 1000).toFixed(1)} s{/if}
            {#if r.cost_usd !== null} · {money(r.cost_usd)}{/if}
          </span>
        </a>
      </li>
    {/each}
  </ol>
</nav>

<style>
  .revisions h2 {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--ink-muted);
  }
  ol {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }
  li a {
    display: block;
    text-decoration: none;
    color: inherit;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.5rem 0.65rem;
  }
  li.selected a {
    border-color: var(--primary);
    box-shadow: inset 3px 0 0 var(--primary);
  }
  .head {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }
  .no {
    font-weight: 600;
    font-size: 0.9rem;
  }
  .current {
    font-size: 0.75rem;
    color: var(--primary-ink);
    background: var(--accent);
    border-radius: 999px;
    padding: 0.05rem 0.45rem;
  }
  .prompt {
    display: block;
    font-size: 0.9rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .meta {
    display: block;
    font-size: 0.78rem;
    color: var(--ink-muted);
    font-variant-numeric: tabular-nums;
  }
</style>
