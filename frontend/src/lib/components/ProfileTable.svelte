<script lang="ts">
  import type { ColumnProfile } from '$lib/api';
  import { formatInt } from '$lib/format';
  import { t } from '$lib/i18n';

  let { columns }: { columns: ColumnProfile[] } = $props();
  const h = t.datasets.detail.profileColumns;

  function summary(c: ColumnProfile): string {
    switch (c.type) {
      case 'integer':
      case 'number':
        return `${c.min} – ${c.max}, mean ${c.mean}, median ${c.median}`;
      case 'date':
        return `${String(c.min).slice(0, 10)} – ${String(c.max).slice(0, 10)}`;
      case 'boolean':
        return `${c.true_count ?? 0} true`;
      default:
        return (c.top_values ?? []).map((v) => `${v.value} (${v.count})`).join(', ');
    }
  }
</script>

<table class="profile">
  <thead>
    <tr>
      <th>{h.name}</th>
      <th>{h.type}</th>
      <th class="num">{h.nulls}</th>
      <th class="num">{h.distinct}</th>
      <th>{h.summary}</th>
    </tr>
  </thead>
  <tbody>
    {#each columns as c (c.name)}
      <tr>
        <td>
          <span class="mono">{c.name}</span>
          {#if c.original_name !== c.name}
            <span class="original" title={h.original}>{c.original_name}</span>
          {/if}
        </td>
        <td><span class="type {c.type}">{t.types[c.type]}</span></td>
        <td class="num">{formatInt(c.null_count)}</td>
        <td class="num">{formatInt(c.distinct_count)}</td>
        <td class="summary">{summary(c)}</td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  .mono {
    font-family: var(--font-mono);
    font-size: 0.9rem;
  }
  .original {
    display: block;
    color: var(--ink-muted);
    font-size: 0.8rem;
  }
  .type {
    font-size: 0.8rem;
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
    background: var(--accent);
    color: var(--primary-ink);
  }
  .type.string {
    background: var(--ground);
    color: var(--ink-muted);
    border: 1px solid var(--line);
  }
  .summary {
    color: var(--ink-muted);
    font-size: 0.9rem;
    max-width: 28rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
