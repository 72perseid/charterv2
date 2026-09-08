<script lang="ts">
  import { goto } from '$app/navigation';
  import { ApiError, charts, type ColumnProfile, type PrivacyLevel } from '$lib/api';
  import { t } from '$lib/i18n/en';

  let {
    datasetId,
    columns,
    privacyLevel
  }: { datasetId: number; columns: ColumnProfile[]; privacyLevel: PrivacyLevel } = $props();
  const s = t.charts.form;

  const quantitative = $derived(columns.filter((c) => c.type === 'integer' || c.type === 'number'));
  let title = $state('');
  let x_field = $state('');
  let y_field = $state('');
  let color_field = $state('');
  let prompt = $state('');
  let error = $state('');
  let busy = $state(false);

  $effect(() => {
    if (!x_field && columns.length) x_field = columns[0].name;
    if (!y_field && quantitative.length) y_field = quantitative[0].name;
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
        prompt: prompt.trim()
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
  <div class="grid">
    <div class="field">
      <label for="x_field">{s.x}</label>
      <select id="x_field" bind:value={x_field} required>
        {#each columns as c (c.name)}
          <option value={c.name}>{c.name} · {t.types[c.type]}</option>
        {/each}
      </select>
    </div>
    <div class="field">
      <label for="y_field">{s.y}</label>
      <select id="y_field" bind:value={y_field} required>
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
  <div class="field">
    <label for="prompt">{s.prompt}</label>
    <textarea id="prompt" rows="3" maxlength="1000" required bind:value={prompt}></textarea>
    <small>{s.promptHint}</small>
    <small class="privacy">
      {s.privacyNote.replace('{level}', t.datasets.privacy.describe[privacyLevel].toLowerCase())}
    </small>
  </div>
  <div class="field">
    <label for="title">{s.chartTitle}</label>
    <input id="title" type="text" maxlength="200" bind:value={title} />
  </div>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit" disabled={busy || !prompt.trim()}>{busy ? s.creating : s.create}</button>
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
  textarea {
    resize: vertical;
  }
</style>
