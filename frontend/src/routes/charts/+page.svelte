<script lang="ts">
  import { invalidateAll } from '$app/navigation';
  import { isBusy } from '$lib/api';
  import StatusChip from '$lib/components/StatusChip.svelte';
  import { formatDate } from '$lib/format';
  import { t } from '$lib/i18n';
  import { onDestroy } from 'svelte';

  let { data } = $props();

  let timer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    clearTimeout(timer);
    if (data.charts.some((c) => c.current_status === null || isBusy(c.current_status))) {
      timer = setTimeout(() => invalidateAll(), 2000);
    }
  });
  onDestroy(() => clearTimeout(timer));
</script>

<svelte:head><title>{t.charts.title} · {t.appName}</title></svelte:head>

<div class="page-head">
  <h1>{t.charts.title}</h1>
</div>

{#if data.charts.length === 0}
  <p class="empty">{t.charts.empty}</p>
{:else}
  <div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>{t.charts.columns.title}</th>
        <th>{t.charts.columns.dataset}</th>
        <th>{t.charts.columns.status}</th>
        <th class="num">{t.charts.columns.revisions}</th>
        <th>{t.charts.columns.updated}</th>
      </tr>
    </thead>
    <tbody>
      {#each data.charts as c (c.id)}
        <tr>
          <td><a href="/charts/{c.id}">{c.title}</a></td>
          <td><a href="/datasets/{c.dataset_id}">{c.dataset_name}</a></td>
          <td><StatusChip status={c.current_status ?? 'pending'} /></td>
          <td class="num">{c.revision_count}</td>
          <td class="nowrap">{formatDate(c.updated_at)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
  </div>
{/if}
