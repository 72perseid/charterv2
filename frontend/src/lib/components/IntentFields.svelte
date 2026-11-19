<script lang="ts">
  // What the chart shows and, optionally, which rows it is limited to: chosen
  // here so it does not depend on how a model reads the request (SPEC §6.3).
  import type { ColumnProfile, Show } from '$lib/api';
  import { t } from '$lib/i18n';

  let {
    columns,
    prefix,
    show = $bindable(),
    filter_field = $bindable(),
    filter_value = $bindable()
  }: {
    columns: ColumnProfile[];
    prefix: string;
    show: Show;
    filter_field: string;
    filter_value: string;
  } = $props();
  const s = t.charts.form;
  const shows: Show[] = ['auto', 'total', 'average', 'count', 'distribution', 'points'];

  const filterable = $derived(columns.filter((c) => c.type !== 'date'));
  const chosen = $derived(columns.find((c) => c.name === filter_field));
  // Values worth offering: every period of a period column, else the most frequent ones.
  const known = $derived(chosen?.order ?? chosen?.top_values?.map((v) => v.value) ?? []);
</script>

<div class="grid">
  <div class="field">
    <label for="{prefix}show">{s.show}</label>
    <select id="{prefix}show" bind:value={show}>
      {#each shows as option (option)}<option value={option}>{s.shows[option]}</option>{/each}
    </select>
  </div>
  <div class="field">
    <label for="{prefix}filter_field">{s.filterField}</label>
    <select
      id="{prefix}filter_field"
      bind:value={filter_field}
      onchange={() => (filter_value = '')}
    >
      <option value="">{s.filterAll}</option>
      {#each filterable as c (c.name)}<option value={c.name}>{c.name}</option>{/each}
    </select>
  </div>
  <div class="field">
    <label for="{prefix}filter_value">{s.filterValue}</label>
    <input
      id="{prefix}filter_value"
      type="text"
      maxlength="200"
      list="{prefix}filter_values"
      disabled={!filter_field}
      required={!!filter_field}
      bind:value={filter_value}
    />
    <datalist id="{prefix}filter_values">
      {#each known as value (value)}<option {value}></option>{/each}
    </datalist>
  </div>
</div>
<small>{s.showHint}</small>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }
  @media (max-width: 48rem) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
  small {
    display: block;
    color: var(--ink-muted);
    font-size: 0.8rem;
    margin: -0.5rem 0 0.75rem;
  }
</style>
