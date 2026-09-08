<script lang="ts">
  import { goto } from '$app/navigation';
  import { ApiError, charts, type ColumnProfile, type RevisionSummary } from '$lib/api';
  import { t } from '$lib/i18n/en';

  let {
    chartId,
    columns,
    parent
  }: { chartId: number; columns: ColumnProfile[]; parent: RevisionSummary } = $props();
  const s = t.charts.page.revise;

  // Pre-filled from the selected revision (SPEC §8); re-seeded when it changes.
  let x_field = $state('');
  let y_field = $state('');
  let color_field = $state('');
  let prompt = $state('');
  let seededFrom = $state<number | null>(null);
  $effect(() => {
    if (seededFrom !== parent.id) {
      x_field = parent.x_field;
      y_field = parent.y_field;
      color_field = parent.color_field ?? '';
      prompt = parent.prompt;
      seededFrom = parent.id;
    }
  });

  let error = $state('');
  let busy = $state(false);

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    error = '';
    busy = true;
    try {
      const revision = await charts.revise(chartId, {
        parent_id: parent.id,
        x_field,
        y_field,
        color_field: color_field || null,
        prompt: prompt.trim()
      });
      await goto(`/charts/${chartId}?revision=${revision.id}`, { invalidateAll: true });
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      busy = false;
    }
  }
</script>

<form class="revise" onsubmit={submit}>
  <h2>{s.title}</h2>
  <p class="lead">{s.lead.replace('{n}', String(parent.revision_no))}</p>
  <div class="grid">
    <div class="field">
      <label for="rx">{t.charts.form.x}</label>
      <select id="rx" bind:value={x_field}>
        {#each columns as c (c.name)}<option value={c.name}>{c.name}</option>{/each}
      </select>
    </div>
    <div class="field">
      <label for="ry">{t.charts.form.y}</label>
      <select id="ry" bind:value={y_field}>
        {#each columns as c (c.name)}<option value={c.name}>{c.name}</option>{/each}
      </select>
    </div>
    <div class="field">
      <label for="rc">{t.charts.form.color}</label>
      <select id="rc" bind:value={color_field}>
        <option value="">{t.charts.form.none}</option>
        {#each columns as c (c.name)}<option value={c.name}>{c.name}</option>{/each}
      </select>
    </div>
  </div>
  <div class="field">
    <label for="rprompt">{s.prompt}</label>
    <textarea id="rprompt" rows="3" maxlength="1000" required bind:value={prompt}></textarea>
  </div>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit" disabled={busy || !prompt.trim()}>{busy ? s.creating : s.submit}</button>
</form>

<style>
  .revise {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
  }
  .lead {
    color: var(--ink-muted);
    font-size: 0.9rem;
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
  textarea {
    resize: vertical;
  }
</style>
