<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { isBusy, type DatasetDetail } from '$lib/api';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import UploadForm from '$lib/components/UploadForm.svelte';
  import { formatDate, formatInt } from '$lib/format';
  import { t } from '$lib/i18n/en';
  import { onDestroy } from 'svelte';

  let { data } = $props();
  let showUpload = $state(false);

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
</script>

<svelte:head><title>{t.datasets.title} · {t.appName}</title></svelte:head>

<div class="page-head">
  <h1>{t.datasets.title}</h1>
  <button type="button" onclick={() => (showUpload = !showUpload)}>{t.datasets.upload}</button>
</div>

{#if showUpload}
  <UploadForm onuploaded={uploaded} oncancel={() => (showUpload = false)} />
{/if}

{#if data.datasets.length === 0}
  <p class="empty">{t.datasets.empty}</p>
{:else}
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
          <td>{formatDate(d.created_at)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
