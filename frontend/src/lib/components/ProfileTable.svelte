<script lang="ts">
  import {
    PERIODO_PERMALINK,
    type ColumnProfile,
    type PeriodChoice,
    type PeriodDates,
    type PeriodRequest
  } from '$lib/api';
  import { formatInt, formatStat } from '$lib/format';
  import { t } from '$lib/i18n';

  let {
    columns,
    requests = {},
    mappings = {},
    onperiod,
    onask,
    onmap,
    ondate
  }: {
    columns: ColumnProfile[];
    requests?: Record<string, PeriodRequest>;
    onperiod?: (column: string, choice: PeriodChoice) => void;
    mappings?: Record<string, Record<string, string>>;
    onask?: (column: string) => void;
    onmap?: (column: string, meanings: Record<string, string | null>) => void;
    ondate?: (column: string, link: PeriodDates | null) => void;
  } = $props();
  const h = t.datasets.detail.profileColumns;
  const p = t.datasets.detail.period;

  // The server refuses to order more distinct values than this (datasets/chronology.py).
  const MAX_PERIOD_VALUES = 200;
  const MAX_PERIOD_LENGTH = 60;

  let editing = $state<string | null>(null);
  let draft = $state('');
  let confirmingAsk = $state(false);
  // The column whose date link is being set from the second button (not yet a period column).
  let dating = $state<string | null>(null);
  let link = $state({ start: '', end: '', bc: false });

  // Only columns of numbers can hold the start and end years.
  const numeric = $derived(columns.filter((c) => c.type === 'integer' || c.type === 'number'));

  function loadLink(c: ColumnProfile) {
    link = {
      start: c.dated_by?.start ?? '',
      end: c.dated_by?.end ?? '',
      bc: c.dated_by?.bc ?? false
    };
  }

  function date(c: ColumnProfile) {
    editing = null;
    if (dating === c.name) {
      dating = null;
      return;
    }
    dating = c.name;
    loadLink(c);
  }

  function close() {
    editing = null;
    dating = null;
  }

  function saveDates(event: SubmitEvent, column: string) {
    event.preventDefault();
    const chosen = { start: link.start, end: link.end || null, bc: link.bc };
    close();
    ondate?.(column, chosen);
  }

  function removeDates(column: string) {
    close();
    ondate?.(column, null);
  }
  // What the user says each value means, keyed by value, for the column being edited.
  let meanings = $state<Record<string, string>>({});

  const matchOf = (c: ColumnProfile, value: string) => c.matches?.find((m) => m.value === value);

  // Only what differs from what is saved; an emptied field removes the mapping.
  function changedMeanings(c: ColumnProfile): Record<string, string | null> {
    const saved = mappings[c.name] ?? {};
    const out: Record<string, string | null> = {};
    for (const value of c.order ?? []) {
      const now = (meanings[value] ?? '').trim();
      if (now !== (saved[value] ?? '')) out[value] = now || null;
    }
    return out;
  }

  const meaningsChanged = (c: ColumnProfile) => Object.keys(changedMeanings(c)).length > 0;

  function saveMeanings(event: SubmitEvent, c: ColumnProfile) {
    event.preventDefault();
    const changed = changedMeanings(c);
    editing = null;
    onmap?.(c.name, changed);
  }

  function years(start: number, stop: number): string {
    const one = (y: number) => (y < 0 ? `${-y} ${p.bc}` : `${p.ad} ${y}`);
    return start === stop ? one(start) : `${one(start)} – ${one(stop)}`;
  }

  // Asking sends cell values to the user's model, so it takes two clicks.
  function ask(column: string) {
    if (!confirmingAsk) {
      confirmingAsk = true;
      return;
    }
    editing = null;
    onask?.(column);
  }

  function summary(c: ColumnProfile): string {
    switch (c.type) {
      case 'integer':
      case 'number':
        return `${formatStat(c.min)} – ${formatStat(c.max)}, mean ${formatStat(c.mean)}, median ${formatStat(c.median)}`;
      case 'date':
        return `${String(c.min).slice(0, 10)} – ${String(c.max).slice(0, 10)}`;
      case 'boolean':
        return `${c.true_count ?? 0} true`;
      case 'period':
        return chronology(c);
      default:
        return (c.top_values ?? []).map((v) => `${v.value} (${v.count})`).join(', ');
    }
  }

  // Oldest first, then the values nothing could place.
  function chronology(c: ColumnProfile): string {
    const unplaced = c.unplaced ?? [];
    const placed = (c.order ?? []).filter((v) => !unplaced.includes(v));
    let text = placed.join(' → ');
    if (unplaced.length) text += `${text ? ' · ' : ''}${p.unplaced}: ${unplaced.join(', ')}`;
    return c.order_source === 'user' ? `${text} (${p.yours})` : text;
  }

  function canBePeriod(c: ColumnProfile): boolean {
    // Long values are notes, citations or links, never period names: no offer on those rows.
    return (
      c.type === 'string' &&
      c.distinct_count >= 2 &&
      c.distinct_count <= MAX_PERIOD_VALUES &&
      (c.max_length ?? 0) <= MAX_PERIOD_LENGTH
    );
  }

  function edit(c: ColumnProfile) {
    if (editing === c.name) {
      editing = null; // the same button closes the panel
      return;
    }
    editing = c.name;
    dating = null;
    loadLink(c);
    confirmingAsk = false;
    meanings = { ...(mappings[c.name] ?? {}) };
    draft = (c.order ?? []).join('\n');
  }

  function choose(column: string, choice: PeriodChoice) {
    editing = null;
    onperiod?.(column, choice);
  }

  function save(event: SubmitEvent, column: string) {
    event.preventDefault();
    const order = draft
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean);
    choose(column, order);
  }
</script>

{#snippet dateForm(c: ColumnProfile)}
  <form class="dates" onsubmit={(e) => saveDates(e, c.name)}>
    <label>
      {p.datesStart}
      <select bind:value={link.start} required>
        <option value="" disabled>…</option>
        {#each numeric as n (n.name)}<option value={n.name}>{n.name}</option>{/each}
      </select>
    </label>
    <label>
      {p.datesEnd}
      <select bind:value={link.end}>
        <option value="">{p.datesNone}</option>
        {#each numeric as n (n.name)}<option value={n.name}>{n.name}</option>{/each}
      </select>
    </label>
    <label class="check"><input type="checkbox" bind:checked={link.bc} /> {p.datesBc}</label>
    <small>{p.datesHint}</small>
    <div class="actions">
      <button type="submit" disabled={!link.start}>{p.datesSave}</button>
      {#if c.dated_by}
        <button type="button" class="quiet" onclick={() => removeDates(c.name)}>
          {p.datesRemove}
        </button>
      {/if}
      <button type="button" class="quiet" onclick={close}>{p.cancel}</button>
    </div>
  </form>
{/snippet}

<div class="table-wrap">
<table class="profile">
  <thead>
    <tr>
      <th>{h.name}</th>
      <th>{h.type}</th>
      <th class="num">{h.nulls}</th>
      <th class="num">{h.distinct}</th>
      <th>{h.summary}</th>
      {#if onperiod}<th></th>{/if}
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
        <td class="summary" title={summary(c)}>{summary(c)}</td>
        {#if onperiod}
          <td class="act">
            {#if c.type === 'period'}
              <button type="button" class="quiet small" onclick={() => edit(c)}>{p.edit}</button>
            {:else if canBePeriod(c)}
              <button type="button" class="offer" onclick={() => choose(c.name, true)}>
                {p.treat}
              </button>
              {#if ondate && numeric.length}
                <button type="button" class="offer" onclick={() => date(c)}>{p.dates}</button>
              {/if}
            {/if}
          </td>
        {/if}
      </tr>
      {#if dating === c.name}
        <tr class="editor">
          <td colspan="6">
            <h3>{p.datesTitle} <span class="mono">{c.name}</span></h3>
            {@render dateForm(c)}
          </td>
        </tr>
      {/if}
      {#if editing === c.name}
        <tr class="editor">
          <td colspan="6">
            {#if c.order_source !== 'user'}
              <h3>{p.placedBy}</h3>
              <p class="note">
                {#if c.dated_by}{p.datedBy}: {c.dated_by.start}{c.dated_by.end
                    ? ` – ${c.dated_by.end}`
                    : ''} · {/if}{#if c.region}{p.datedFor}: {c.region} · {/if}{p.snapshot}
                {c.periodo_snapshot}
              </p>
              <form onsubmit={(e) => saveMeanings(e, c)}>
                <table class="matches">
                  <tbody>
                    {#each c.order ?? [] as value (value)}
                      {@const m = matchOf(c, value)}
                      <tr>
                        <td>{value}</td>
                        <td class="num">{m ? years(m.start, m.stop) : '—'}</td>
                        <td>
                          {#if m?.id}
                            <a href={PERIODO_PERMALINK + m.id} target="_blank" rel="noreferrer">
                              {m.label}
                            </a>
                          {:else if m?.label}
                            {m.label}
                          {/if}
                          <span class="via">
                            {#if !m}
                              {mappings[c.name]?.[value] ? p.notRead : p.notPlaced}
                            {:else}
                              {m.via === 'model' && !m.id ? p.modelEstimate : p.via[m.via]}{m.source
                                ? ` · ${m.source}`
                                : ''}{m.varies ? ` · ${p.varies}` : ''}
                            {/if}
                          </span>
                        </td>
                        <td>
                          <input
                            type="text"
                            maxlength="120"
                            aria-label="{p.means}: {value}"
                            placeholder={m ? '' : p.meansPlaceholder}
                            bind:value={meanings[value]}
                          />
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
                <small>{p.meansHint}</small>
                <div class="actions">
                  <button type="submit" disabled={!meaningsChanged(c)}>{p.saveMappings}</button>
                </div>
              </form>
            {/if}
            {#if requests[c.name]?.error}
              <p class="error" role="alert">{p.askFailed}: {requests[c.name].error}</p>
            {/if}
            {#if onask && c.order_source !== 'user' && c.unplaced?.length}
              <div class="ask">
                <button type="button" class="quiet" onclick={() => ask(c.name)}>
                  {confirmingAsk ? p.askConfirm : `${p.ask} (${c.unplaced.length})`}
                </button>
                <small>{p.askHint}</small>
              </div>
            {/if}
            {#if ondate && numeric.length && c.order_source !== 'user'}
              <details open={!!c.dated_by}>
                <summary>{p.dates}</summary>
                {@render dateForm(c)}
              </details>
            {/if}
            <details open={c.order_source === 'user'}>
              <summary>{p.typeOrder}</summary>
            <form class="order" onsubmit={(e) => save(e, c.name)}>
              <label for="period-order">{p.editorLabel} <span class="mono">{c.name}</span></label>
              <textarea
                id="period-order"
                rows={Math.min(Math.max((c.order ?? []).length, 3), 14)}
                bind:value={draft}
              ></textarea>
              <small>{p.editorHint}</small>
              <div class="actions">
                <button type="submit">{p.save}</button>
                <button type="button" class="quiet" onclick={() => choose(c.name, null)}>
                  {p.detect}
                </button>
                <button type="button" class="quiet" onclick={() => choose(c.name, false)}>
                  {p.notPeriod}
                </button>
                <button type="button" class="quiet" onclick={close}>
                  {p.cancel}
                </button>
              </div>
            </form>
            </details>
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</table>
</div>

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
    max-width: 22rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .act {
    text-align: right;
    white-space: nowrap;
  }
  .small {
    font-size: 0.8rem;
    padding: 0.15rem 0.5rem;
  }
  /* Offered on every text column, so it is a quiet link, not a row of buttons. */
  .offer {
    background: none;
    border: 0;
    padding: 0.1rem 0.3rem;
    font-size: 0.8rem;
    color: var(--ink-muted);
    text-decoration: underline;
    text-underline-offset: 2px;
  }
  .offer:hover {
    color: var(--primary-ink);
  }
  .editor h3 {
    font-size: 0.95rem;
    margin: 0.5rem 0 0.1rem;
  }
  .note {
    color: var(--ink-muted);
    font-size: 0.8rem;
    margin: 0 0 0.4rem;
  }
  .matches {
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
  }
  .matches td {
    padding: 0.2rem 0.75rem 0.2rem 0;
    vertical-align: top;
  }
  .via {
    display: block;
    color: var(--ink-muted);
    font-size: 0.8rem;
  }
  .ask {
    display: grid;
    gap: 0.3rem;
    justify-items: start;
    max-width: 36rem;
    margin-bottom: 0.75rem;
  }
  .editor form {
    display: grid;
    gap: 0.4rem;
    padding: 0.25rem 0 0.5rem;
  }
  .editor form.order {
    max-width: 28rem;
  }
  .editor form.dates {
    max-width: 36rem;
  }
  .dates label {
    display: grid;
    gap: 0.15rem;
    font-size: 0.9rem;
  }
  .dates label.check {
    display: flex;
    gap: 0.4rem;
    align-items: center;
  }
  .matches input {
    min-width: 14rem;
    font-size: 0.85rem;
    padding: 0.15rem 0.4rem;
  }
  .editor summary {
    cursor: pointer;
    color: var(--ink-muted);
    font-size: 0.9rem;
    margin: 0.25rem 0;
  }
  .editor textarea {
    font-family: var(--font-mono);
    font-size: 0.9rem;
  }
  .editor small {
    color: var(--ink-muted);
    font-size: 0.8rem;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
</style>
