<script lang="ts">
  import { goto } from '$app/navigation';
  import { ApiError, charts, modelConfig, type ColumnProfile, type PrivacyLevel, type Show } from '$lib/api';
  import { onMount } from 'svelte';
  import IntentFields from '$lib/components/IntentFields.svelte';
  import { t } from '$lib/i18n';

  let {
    datasetId,
    columns,
    privacyLevel
  }: { datasetId: number; columns: ColumnProfile[]; privacyLevel: PrivacyLevel } = $props();
  const s = t.charts.form;

  let title = $state('');
  let x_field = $state('');
  let y_field = $state('');
  let color_field = $state('');
  let prompt = $state('');
  let show = $state<Show>('auto');
  let filter_field = $state('');
  let filter_value = $state('');
  let error = $state('');
  let busy = $state(false);

  // Whether a model is connected; null until known. Asked here so the form can say so
  // before a chart is created and fails for that reason.
  let connected = $state<boolean | null>(null);
  onMount(async () => {
    try {
      const config = await modelConfig.get();
      connected = Boolean(config.base_url && config.model);
    } catch {
      connected = null;
    }
  });

  // A period column is what the x axis is for in most charts made here, so it is
  // offered. Nothing else is guessed: the first column of a table is usually an
  // identifier, and a chart of the wrong columns costs a request.
  $effect(() => {
    if (!x_field) x_field = columns.find((c) => c.type === 'period')?.name ?? '';
  });

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    error = '';
    busy = true;
    try {
      const chart = await charts.create({
        dataset_id: datasetId,
        title: title.trim(),
        x_field,
        y_field,
        color_field: color_field || null,
        prompt: prompt.trim(),
        show,
        filter_field: filter_field || null,
        filter_value: filter_field ? filter_value.trim() : null
      });
      await goto(`/charts/${chart.id}`);
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      busy = false;
    }
  }
</script>

<form class="chart-form" onsubmit={submit}>
  <h2>{s.title}</h2>
  {#if connected === false}
    <p class="no-model" role="status">{s.noModel} <a href="/settings">{s.noModelLink}</a></p>
  {/if}
  <div class="grid">
    <div class="field">
      <label for="x_field">{s.x}</label>
      <select id="x_field" bind:value={x_field} required>
        <option value="" disabled>{s.choose}</option>
        {#each columns as c (c.name)}
          <option value={c.name}>{c.name} · {t.types[c.type]}</option>
        {/each}
      </select>
    </div>
    <div class="field">
      <label for="y_field">{s.y}</label>
      <select id="y_field" bind:value={y_field} required>
        <option value="" disabled>{s.choose}</option>
        {#each columns as c (c.name)}
          <option value={c.name}>{c.name} · {t.types[c.type]}</option>
        {/each}
      </select>
    </div>
    <div class="field">
      <label for="color_field">{s.color}</label>
      <select id="color_field" bind:value={color_field}>
        <option value="">{s.none}</option>
        {#each columns as c (c.name)}
          <option value={c.name}>{c.name} · {t.types[c.type]}</option>
        {/each}
      </select>
    </div>
  </div>
  <IntentFields {columns} prefix="new_" bind:show bind:filter_field bind:filter_value />
  <div class="field">
    <label for="prompt">{s.prompt}</label>
    <textarea id="prompt" rows="3" maxlength="1000" required bind:value={prompt}></textarea>
    <small>{s.promptHint}</small>
    <small class="privacy">
      {s.privacyNote.replace('{level}', t.datasets.privacy.levels[privacyLevel])}
      {t.datasets.privacy.describe[privacyLevel]}
    </small>
  </div>
  <div class="field">
    <label for="title">{s.chartTitle}</label>
    <input id="title" type="text" maxlength="200" bind:value={title} />
  </div>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit" disabled={busy || !prompt.trim() || !x_field || !y_field}>{busy ? s.creating : s.create}</button>
</form>

<style>
  .chart-form {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
  }
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
    margin-top: 0.25rem;
  }
  .privacy {
    color: var(--primary-ink);
  }
  .no-model {
    border-left: 3px solid var(--warning);
    padding: 0.4rem 0.75rem;
    margin: 0.5rem 0 1rem;
    font-size: 0.9rem;
  }
  textarea {
    resize: vertical;
  }
</style>
