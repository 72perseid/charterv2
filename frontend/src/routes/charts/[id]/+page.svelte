<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { ApiError, charts, isBusy } from '$lib/api';
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import { formatInt } from '$lib/format';
  import { t } from '$lib/i18n/en';
  import { onDestroy } from 'svelte';

  let { data } = $props();
  const s = t.charts.page;
  const chart = $derived(data.chart);
  const rev = $derived(data.revision);

  let tab: 'chart' | 'spec' | 'request' = $state('chart');
  let error = $state('');
  let confirmingDelete = $state(false);

  // Poll every 2 s while the shown revision is pending or running (SPEC §2).
  let timer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    clearTimeout(timer);
    if (rev && isBusy(rev.status)) timer = setTimeout(() => invalidateAll(), 2000);
  });
  onDestroy(() => clearTimeout(timer));

  async function remove() {
    if (!confirmingDelete) {
      confirmingDelete = true;
      return;
    }
    try {
      await charts.remove(chart.id);
      await goto('/charts');
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
      confirmingDelete = false;
    }
  }

  const pretty = (value: unknown) => JSON.stringify(value, null, 2);
  const money = (usd: number) => '$' + (usd < 0.01 ? usd.toFixed(5) : usd.toFixed(3));
</script>

<svelte:head><title>{chart.title} · {t.appName}</title></svelte:head>

<div class="page-head">
  <div>
    <h1>{chart.title}</h1>
    <p class="meta">
      {s.dataset}: <a href="/datasets/{chart.dataset_id}">{chart.dataset_name}</a>
      {#if rev}· {s.revision} {rev.revision_no} · {rev.x_field} × {rev.y_field}{#if rev.color_field} · {rev.color_field}{/if}{/if}
    </p>
  </div>
  <div class="head-actions">
    {#if rev}<StatusChip status={rev.status} />{/if}
    <button type="button" class="quiet danger" onclick={remove}>
      {confirmingDelete ? s.confirmDelete : s.delete}
    </button>
  </div>
</div>

{#if error}<p class="error" role="alert">{error}</p>{/if}

{#if rev}
  <p class="prompt">“{rev.prompt}”</p>

  {#if rev.status === 'pending'}
    <p class="empty">{s.waiting}</p>
  {:else if rev.status === 'running'}
    <p class="empty">{s.running}</p>
  {:else if rev.status === 'failed'}
    <div class="failed"><strong>{s.failed}.</strong> {rev.error_message}</div>
  {/if}

  {#if rev.status === 'done' || rev.status === 'failed'}
    <nav class="tabs" aria-label="views">
      {#if rev.status === 'done'}
        <button type="button" class:active={tab === 'chart'} onclick={() => (tab = 'chart')}>{s.tabs.chart}</button>
        <button type="button" class:active={tab === 'spec'} onclick={() => (tab = 'spec')}>{s.tabs.spec}</button>
      {/if}
      <button type="button" class:active={tab === 'request' || rev.status === 'failed'} onclick={() => (tab = 'request')}>{s.tabs.request}</button>
    </nav>

    {#if tab === 'chart' && rev.status === 'done' && rev.spec && data.rows}
      <ChartCanvas spec={rev.spec} rows={data.rows.rows} />
      {#if rev.corrections.length}
        <details class="note">
          <summary>{s.corrections} ({rev.corrections.length})</summary>
          <ul>{#each rev.corrections as c, i (i)}<li>{c}</li>{/each}</ul>
        </details>
      {/if}
    {:else if tab === 'spec' && rev.status === 'done'}
      <pre class="code">{pretty(rev.spec)}</pre>
    {:else}
      <section class="record">
        <dl>
          <dt>{s.record.model}</dt><dd>{rev.model}</dd>
          <dt>{s.record.endpoint}</dt><dd>{rev.endpoint_host}</dd>
          <dt>{s.record.temperature}</dt><dd>{rev.temperature}</dd>
          <dt>{s.record.seed}</dt><dd>{rev.seed}</dd>
          <dt>{s.record.promptVersion}</dt><dd>{rev.prompt_version}</dd>
          <dt>{s.record.appVersion}</dt><dd>{rev.app_version}</dd>
          <dt>{s.record.duration}</dt><dd>{rev.duration_ms !== null ? `${formatInt(rev.duration_ms)} ms` : '—'}</dd>
          <dt>{s.record.tokens}</dt>
          <dd>
            {#if rev.usage}
              {formatInt(rev.usage.total_tokens ?? 0)}
              <span class="muted">
                ({s.record.tokensDetail
                  .replace('{prompt}', formatInt(rev.usage.prompt_tokens ?? 0))
                  .replace('{completion}', formatInt(rev.usage.completion_tokens ?? 0))
                  .replace('{reasoning}', rev.usage.reasoning_tokens ? s.record.reasoning.replace('{n}', formatInt(rev.usage.reasoning_tokens)) : '')})
              </span>
            {:else}—{/if}
          </dd>
          <dt>{s.record.cost}</dt>
          <dd>
            {#if rev.cost_usd !== null}
              {money(rev.cost_usd)}
            {:else if rev.cost_at_current_prices !== null}
              {money(rev.cost_at_current_prices)} <span class="muted">({s.record.costAtCurrent})</span>
            {:else}<span class="muted">{s.record.costUnknown}</span>{/if}
          </dd>
          <dt>{s.record.attempt}</dt><dd>{rev.request?.attempt ?? rev.attempts}</dd>
        </dl>
        {#if rev.request?.adjustments.length}
          <p class="adjust">{s.adjustments}: {rev.request.adjustments.join(', ')}</p>
        {/if}
        {#if rev.request}
          <h3>{s.messages}</h3>
          {#each rev.request.messages as m, i (i)}
            <div class="msg">
              <span class="role">{m.role}</span>
              <pre class="code">{m.content}</pre>
            </div>
          {/each}
          <h3>{s.response}</h3>
          <pre class="code">{rev.response_text}</pre>
        {/if}
      </section>
    {/if}
  {/if}
{/if}

<style>
  .meta {
    color: var(--ink-muted);
    margin: 0;
  }
  .head-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .danger {
    color: var(--destructive);
  }
  .prompt {
    font-style: italic;
    color: var(--ink-muted);
  }
  .failed {
    border: 1px solid var(--destructive);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    background: var(--surface);
    margin-bottom: 1rem;
  }
  .tabs {
    display: flex;
    gap: 0.25rem;
    border-bottom: 1px solid var(--line);
    margin-bottom: 1rem;
  }
  .tabs button {
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: var(--ink-muted);
    padding: 0.5rem 0.75rem;
  }
  .tabs button.active {
    color: var(--ink);
    border-bottom-color: var(--primary);
  }
  .code {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    font-family: var(--font-mono);
    font-size: 0.8rem;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 32rem;
    overflow: auto;
    margin: 0 0 0.75rem;
  }
  .note {
    margin-top: 0.75rem;
    color: var(--ink-muted);
    font-size: 0.9rem;
  }
  .record dl {
    display: grid;
    grid-template-columns: auto 1fr auto 1fr auto 1fr;
    gap: 0.3rem 1rem;
    font-size: 0.9rem;
    margin: 0 0 1rem;
  }
  .record dt {
    color: var(--ink-muted);
  }
  .record dd {
    margin: 0;
    font-variant-numeric: tabular-nums;
  }
  .muted {
    color: var(--ink-muted);
  }
  .adjust {
    color: var(--warning);
    font-size: 0.9rem;
  }
  .msg .role {
    display: inline-block;
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--ink-muted);
    margin-bottom: 0.25rem;
  }
  h3 {
    font-size: 1rem;
    margin: 1rem 0 0.5rem;
  }
</style>
