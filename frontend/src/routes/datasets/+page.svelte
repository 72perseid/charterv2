<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { ApiError, datasets, isBusy, type DatasetDetail } from '$lib/api';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import UploadForm from '$lib/components/UploadForm.svelte';
  import { formatDate, formatInt } from '$lib/format';
  import { language, t } from '$lib/i18n';
  import { onDestroy } from 'svelte';

  let { data } = $props();
  let showUpload = $state(false);
  let adding = $state(false);
  let error = $state('');

  // Poll every 2 s while any dataset is still being parsed (SPEC §2, status updates).
  let timer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    clearTimeout(timer);
    if (data.datasets.some((d) => isBusy(d.status))) {
      timer = setTimeout(() => invalidateAll(), 2000);
    }
  });
  onDestroy(() => clearTimeout(timer));

  async function uploaded(dataset: DatasetDetail) {
    showUpload = false;
    await goto(`/datasets/${dataset.id}`);
  }

  async function addExample() {
    error = '';
    adding = true;
    try {
      await uploaded(await datasets.example(language));
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      adding = false;
    }
  }
</script>

<svelte:head><title>{t.datasets.title} · {t.appName}</title></svelte:head>

<div class="page-head">
  <h1>{t.datasets.title}</h1>
  <div class="actions">
    <button
      type="button"
      class="quiet"
      title={t.datasets.exampleTitle}
      disabled={adding}
      onclick={addExample}
    >
      {adding ? t.datasets.exampleAdding : t.datasets.example}
    </button>
    <button type="button" onclick={() => (showUpload = !showUpload)}>{t.datasets.upload}</button>
  </div>
</div>

{#if error}<p class="error" role="alert">{error}</p>{/if}

{#if showUpload}
  <UploadForm onuploaded={uploaded} oncancel={() => (showUpload = false)} />
{/if}

{#if data.datasets.length === 0}
  <p class="empty">{t.datasets.empty}</p>
{:else}
  <div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>{t.datasets.columns.name}</th>
        <th class="num">{t.datasets.columns.rows}</th>
        <th class="num">{t.datasets.columns.columns}</th>
        <th>{t.datasets.columns.status}</th>
        <th>{t.datasets.columns.created}</th>
      </tr>
    </thead>
    <tbody>
      {#each data.datasets as d (d.id)}
        <tr>
          <td><a href="/datasets/{d.id}">{d.name}</a></td>
          <td class="num">{d.status === 'done' ? formatInt(d.row_count) : ''}</td>
          <td class="num">{d.status === 'done' ? formatInt(d.column_count) : ''}</td>
          <td><StatusChip status={d.status} /></td>
          <td class="nowrap">{formatDate(d.created_at)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
  </div>
{/if}

<style>
  .actions {
    display: flex;
    gap: 0.5rem;
  }
</style>
