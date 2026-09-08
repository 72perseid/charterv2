<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { ApiError, charts, isBusy, type ColumnType } from '$lib/api';
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import DataTable from '$lib/components/DataTable.svelte';
  import RevisionForm from '$lib/components/RevisionForm.svelte';
  import RevisionList from '$lib/components/RevisionList.svelte';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import { saveBlob, saveText, slug } from '$lib/download';
  import { formatInt } from '$lib/format';
  import { t } from '$lib/i18n/en';
  import { onDestroy } from 'svelte';
  import type { Result } from 'vega-embed';

  let { data } = $props();
  const s = t.charts.page;
  const chart = $derived(data.chart);
  const rev = $derived(data.revision);
  const columns = $derived(data.dataset.profile.columns ?? []);
  const types = $derived(
    Object.fromEntries(columns.map((c) => [c.name, c.type])) as Record<string, ColumnType>
  );

  let tab: 'chart' | 'data' | 'spec' | 'request' = $state('chart');
  let error = $state('');
  let confirmingDelete = $state(false);
  let view: Result | null = $state(null);

  // Poll every 2 s while the shown revision is pending or running (SPEC §2).
  let timer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    clearTimeout(timer);
    if (rev && isBusy(rev.status)) timer = setTimeout(() => invalidateAll(), 2000);
  });
  onDestroy(() => clearTimeout(timer));

  async function run(action: () => Promise<unknown>) {
    error = '';
    try {
      await action();
      await invalidateAll();
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    }
  }

  const makeCurrent = () =>
    rev && run(() => charts.patch(chart.id, { current_revision_id: rev.id }));

  async function remove() {
    if (!confirmingDelete) {
      confirmingDelete = true;
      return;
    }
    error = '';
    try {
      await charts.remove(chart.id);
      await goto('/charts');
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
      confirmingDelete = false;
    }
  }

  const base = $derived(`${slug(chart.title)}-r${rev?.revision_no ?? 0}`);

  async function exportImage(kind: 'png' | 'svg') {
    if (!view) return;
    if (kind === 'svg') {
      saveText(await view.view.toSVG(), `${base}.svg`, 'image/svg+xml');
      return;
    }
    const url = await view.view.toImageURL('png', 2);
    saveBlob(await (await fetch(url)).blob(), `${base}.png`);
  }

  const exportSpec = () => rev?.spec && saveText(JSON.stringify(rev.spec, null, 2), `${base}.vl.json`);

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
    {#if rev && rev.status === 'done' && rev.id !== chart.current_revision_id}
      <button type="button" class="quiet" onclick={makeCurrent}>{s.makeCurrent}</button>
    {/if}
    <button type="button" class="quiet danger" onclick={remove}>
      {confirmingDelete ? s.confirmDelete : s.delete}
    </button>
  </div>
</div>

{#if error}<p class="error" role="alert">{error}</p>{/if}

<div class="layout">
  <div class="main">
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
            <button type="button" class:active={tab === 'data'} onclick={() => (tab = 'data')}>{s.tabs.data}</button>
            <button type="button" class:active={tab === 'spec'} onclick={() => (tab = 'spec')}>{s.tabs.spec}</button>
          {/if}
          <button type="button" class:active={tab === 'request' || rev.status === 'failed'} onclick={() => (tab = 'request')}>{s.tabs.request}</button>
        </nav>

        {#if tab === 'chart' && rev.status === 'done' && rev.spec && data.rows}
          <ChartCanvas spec={rev.spec} rows={data.rows.rows} onready={(r) => (view = r)} />
          {#if rev.corrections.length}
            <details class="note">
              <summary>{s.corrections} ({rev.corrections.length})</summary>
              <ul>{#each rev.corrections as c, i (i)}<li>{c}</li>{/each}</ul>
            </details>
          {/if}
        {:else if tab === 'data' && rev.status === 'done' && data.rows}
          <p class="muted small">{s.dataRows.replace('{shown}', formatInt(Math.min(100, data.rows.rows.length))).replace('{total}', formatInt(data.rows.total))}</p>
          <DataTable columns={data.rows.columns} rows={data.rows.rows.slice(0, 100)} {types} />
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
              <dt>{s.record.attempt}</dt><dd>{rev.request?.attempt ?? rev.attempts}</dd>
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

      {#if rev.status === 'done' || rev.status === 'failed'}
        <section class="export">
          <h2>{s.export.title}</h2>
          <div class="buttons">
            <button type="button" class="quiet" onclick={() => exportImage('png')} disabled={!view || rev.status !== 'done'}>{s.export.png}</button>
            <button type="button" class="quiet" onclick={() => exportImage('svg')} disabled={!view || rev.status !== 'done'}>{s.export.svg}</button>
            <button type="button" class="quiet" onclick={exportSpec} disabled={!rev.spec}>{s.export.json}</button>
            <a class="button quiet" href={charts.exportUrl(chart.id)} download="charter-chart-{chart.id}.json">{s.export.bundle}</a>
          </div>
          <small class="muted">{s.export.bundleHint}</small>
        </section>

        <RevisionForm chartId={chart.id} {columns} parent={rev} />
      {/if}
    {/if}
  </div>

  <aside class="side">
    <RevisionList chartId={chart.id} revisions={chart.revisions} selectedId={rev?.id ?? null} currentId={chart.current_revision_id} />
  </aside>
</div>

<style>
  .meta {
    color: var(--ink-muted);
    margin: 0;
  }
  .head-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  .danger {
    color: var(--destructive);
  }
  .layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 18rem;
    gap: 1.5rem;
    align-items: start;
  }
  @media (max-width: 56rem) {
    .layout {
      grid-template-columns: 1fr;
    }
  }
  .main > * + * {
    margin-top: 1rem;
  }
  .prompt {
    font-style: italic;
    color: var(--ink-muted);
    margin: 0;
  }
  .failed {
    border: 1px solid var(--destructive);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    background: var(--surface);
  }
  .tabs {
    display: flex;
    gap: 0.25rem;
    border-bottom: 1px solid var(--line);
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
    color: var(--ink-muted);
    font-size: 0.9rem;
  }
  .record dl {
    display: grid;
    grid-template-columns: auto 1fr auto 1fr;
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
  .small {
    font-size: 0.85rem;
    margin: 0;
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
  .export {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.75rem 1.25rem 0.9rem;
  }
  .export h2 {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--ink-muted);
  }
  .buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.4rem;
  }
  .side {
    position: sticky;
    top: 1rem;
  }
</style>
