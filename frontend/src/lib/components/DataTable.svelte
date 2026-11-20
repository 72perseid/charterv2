<script lang="ts">
  import type { Cell, ColumnType } from '$lib/api';

  let {
    columns,
    rows,
    types = {}
  }: { columns: string[]; rows: Record<string, Cell>[]; types?: Record<string, ColumnType> } =
    $props();

  function show(value: Cell, type: ColumnType | undefined): string {
    if (value === null || value === undefined) return '';
    if (type === 'date' && typeof value === 'string') return value.replace('T00:00:00', '');
    return String(value);
  }

  function numeric(type: ColumnType | undefined): boolean {
    return type === 'integer' || type === 'number';
  }
</script>

<div class="scroll">
  <table>
    <thead>
      <tr>
        {#each columns as column (column)}
          <th class:num={numeric(types[column])}>{column}</th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each rows as row, i (i)}
        <tr>
          {#each columns as column (column)}
            <td class:num={numeric(types[column])} class:empty-cell={row[column] === null}>
              {show(row[column], types[column])}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .scroll {
    overflow: auto;
    max-height: 30rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
  }
  table {
    border: 0;
  }
  thead th {
    position: sticky;
    top: 0;
    background: var(--surface);
    box-shadow: inset 0 -1px 0 var(--line);
  }
  th,
  td {
    white-space: nowrap;
    font-size: 0.9rem;
  }
  .empty-cell {
    background: repeating-linear-gradient(45deg, transparent 0 4px, var(--ground) 4px 8px);
  }
</style>
