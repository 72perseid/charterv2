<script lang="ts">
  import StatusChip from '$lib/components/StatusChip.svelte';
  import { formatDate, formatInt } from '$lib/format';
  import { t } from '$lib/i18n/en';

  let { data } = $props();
</script>

<svelte:head><title>{t.datasets.title} · {t.appName}</title></svelte:head>

<div class="page-head">
  <h1>{t.datasets.title}</h1>
  <!-- Upload arrives in build step 2. -->
  <button type="button" disabled>{t.datasets.upload}</button>
</div>

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
          <td class="num">{formatInt(d.row_count)}</td>
          <td class="num">{formatInt(d.column_count)}</td>
          <td><StatusChip status={d.status} /></td>
          <td>{formatDate(d.created_at)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
