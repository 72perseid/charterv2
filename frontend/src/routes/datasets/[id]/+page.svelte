<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { ApiError, datasets, isBusy, type ColumnType, type PrivacyLevel } from '$lib/api';
  import ChartForm from '$lib/components/ChartForm.svelte';
  import DataTable from '$lib/components/DataTable.svelte';
  import PrivacyPicker from '$lib/components/PrivacyLevel.svelte';
  import ProfileTable from '$lib/components/ProfileTable.svelte';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import { formatInt } from '$lib/format';
  import { t } from '$lib/i18n/en';
  import { onDestroy } from 'svelte';

  let { data } = $props();
  const d = $derived(data.dataset);
  const s = t.datasets.detail;

  let error = $state('');
  let confirmingDelete = $state(false);
  let headerRow = $state<number | null>(null);
  let sheet = $state<string | null>(null);

  const types = $derived(
    Object.fromEntries((d.profile.columns ?? []).map((c) => [c.name, c.type])) as Record<
      string,
      ColumnType
    >
  );

  let timer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    clearTimeout(timer);
    if (isBusy(d.status)) timer = setTimeout(() => invalidateAll(), 2000);
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

  const setPrivacy = (level: PrivacyLevel) => run(() => datasets.patch(d.id, { privacy_level: level }));

  function applyParse(event: SubmitEvent) {
    event.preventDefault();
    const fields: { sheet?: string; header_row?: number } = {};
    if (sheet !== null) fields.sheet = sheet;
    if (headerRow !== null) fields.header_row = headerRow;
    run(() => datasets.patch(d.id, fields));
  }

  async function remove() {
    if (!confirmingDelete) {
      confirmingDelete = true;
      return;
    }
    error = '';
    try {
      await datasets.remove(d.id);
      await goto('/datasets');
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
      confirmingDelete = false;
    }
  }
</script>

<svelte:head><title>{d.name} · {t.appName}</title></svelte:head>

<div class="page-head">
  <div>
    <h1>{d.name}</h1>
    <p class="meta">
      {s.file}: {d.original_filename}
      {#if d.status === 'done'}
        · {formatInt(d.row_count)} × {formatInt(d.column_count)}
      {/if}
    </p>
  </div>
  <div class="head-actions">
    <StatusChip status={d.status} />
    <a class="button quiet" href={datasets.downloadUrl(d.id)}>{s.download}</a>
    <button type="button" class="quiet danger" onclick={remove}>
      {confirmingDelete ? s.confirmDelete : s.delete}
    </button>
    <a class="button" href="#new-chart" class:disabled={d.status !== 'done'}>{s.newChart}</a>
  </div>
</div>

{#if error}<p class="error" role="alert">{error}</p>{/if}

{#if isBusy(d.status)}
  <p class="empty">{s.parsing}</p>
{:else if d.status === 'failed'}
  <div class="failed">
    <strong>{s.failed}.</strong>
    {d.error_message}
  </div>
{/if}

<section class="columns-2">
  <form class="parse" onsubmit={applyParse}>
    <h2>{s.parse}</h2>
    <dl>
      {#if d.parse_options.kind === 'text'}
        <dt>{s.encoding}</dt>
        <dd>{d.parse_options.encoding}</dd>
        <dt>{s.delimiter}</dt>
        <dd><code>{d.parse_options.delimiter === '\t' ? 'tab' : d.parse_options.delimiter}</code></dd>
        <dt>{s.decimal}</dt>
        <dd><code>{d.parse_options.decimal}</code></dd>
      {/if}
      {#if d.parse_options.sheets}
        <dt><label for="sheet">{s.sheet}</label></dt>
        <dd>
          <select id="sheet" value={sheet ?? d.parse_options.sheet} onchange={(e) => (sheet = e.currentTarget.value)}>
            {#each d.parse_options.sheets as name (name)}
              <option value={name}>{name}</option>
            {/each}
          </select>
        </dd>
      {/if}
      <dt><label for="header_row">{s.headerRow}</label></dt>
      <dd>
        <input
          id="header_row"
          type="number"
          min="0"
          max="1000"
          value={headerRow ?? d.parse_options.header_row ?? 0}
          oninput={(e) => (headerRow = Number(e.currentTarget.value))}
        />
        <small>{s.headerRowHint}</small>
      </dd>
    </dl>
    <button type="submit" class="quiet" disabled={isBusy(d.status) || (sheet === null && headerRow === null)}>
      {s.apply}
    </button>
  </form>

  <PrivacyPicker value={d.privacy_level} onchange={setPrivacy} />
</section>

{#if d.status === 'done' && d.profile.columns}
  <section id="new-chart">
    <ChartForm datasetId={d.id} columns={d.profile.columns} privacyLevel={d.privacy_level} />
  </section>

  <section>
    <h2>{s.profile}</h2>
    <ProfileTable columns={d.profile.columns} />
  </section>

  {#if data.rows}
    <section>
      <h2>{s.rows} <span class="count">{data.rows.rows.length} {s.rowsOf} {formatInt(data.rows.total)}</span></h2>
      <DataTable columns={data.rows.columns} rows={data.rows.rows} {types} />
    </section>
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
    flex-wrap: wrap;
  }
  .danger {
    color: var(--destructive);
  }
  .disabled {
    pointer-events: none;
    opacity: 0.6;
  }
  .failed {
    border: 1px solid var(--destructive);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    background: var(--surface);
    margin-bottom: 1.5rem;
  }
  section {
    margin: 1.5rem 0;
  }
  .columns-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    align-items: start;
  }
  @media (max-width: 48rem) {
    .columns-2 {
      grid-template-columns: 1fr;
    }
  }
  .parse {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
  }
  dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.4rem 1rem;
    margin: 0 0 0.75rem;
    align-items: center;
  }
  dt {
    color: var(--ink-muted);
    font-size: 0.9rem;
  }
  dd {
    margin: 0;
  }
  dd input,
  dd select {
    max-width: 14rem;
  }
  dd small {
    display: block;
    color: var(--ink-muted);
    font-size: 0.8rem;
  }
  .count {
    font-weight: normal;
    color: var(--ink-muted);
    font-size: 0.9rem;
  }
</style>
