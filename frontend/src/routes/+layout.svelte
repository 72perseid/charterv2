<script lang="ts">
  import '../app.css';
  import AppShell from '$lib/components/AppShell.svelte';
  import { session } from '$lib/session.svelte';

  let { children } = $props();
</script>

{#if session.user}
  <AppShell user={session.user}>
    {@render children()}
  </AppShell>
{:else}
  {@render children()}
{/if}
