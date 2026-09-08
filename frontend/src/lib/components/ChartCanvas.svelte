<script lang="ts">
  // Wraps vega-embed (SPEC §8). Receives the stored spec and the rows, and
  // supplies the rows as data.values at render time; the spec itself never
  // carries data.
  import embed, { type Result } from 'vega-embed';
  import type { Cell } from '$lib/api';

  let {
    spec,
    rows,
    onready
  }: {
    spec: Record<string, unknown>;
    rows: Record<string, Cell>[];
    onready?: (result: Result) => void;
  } = $props();

  let host: HTMLDivElement | undefined = $state();
  let renderError = $state('');

  $effect(() => {
    if (!host) return;
    const withData = { ...spec, data: { values: rows }, width: 'container' as const };
    let result: Result | undefined;
    let cancelled = false;
    renderError = '';
    embed(host, withData as Parameters<typeof embed>[1], {
      actions: { export: true, source: false, compiled: false, editor: false },
      renderer: 'svg'
    })
      .then((r) => {
        if (cancelled) {
          r.finalize();
          return;
        }
        result = r;
        onready?.(r);
      })
      .catch((e: unknown) => {
        renderError = e instanceof Error ? e.message : String(e);
      });
    return () => {
      cancelled = true;
      result?.finalize();
    };
  });
</script>

<div class="canvas">
  <div bind:this={host} class="host"></div>
  {#if renderError}<p class="error" role="alert">{renderError}</p>{/if}
</div>

<style>
  .canvas {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1rem;
  }
  .host {
    width: 100%;
    min-height: 20rem;
  }
</style>
