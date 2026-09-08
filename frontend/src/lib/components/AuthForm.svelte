<script lang="ts">
  import { ApiError } from '$lib/api';
  import { t } from '$lib/i18n';
  import LanguageSwitch from '$lib/components/LanguageSwitch.svelte';

  let {
    mode,
    onsubmit
  }: {
    mode: 'login' | 'register';
    onsubmit: (fields: { email: string; password: string; display_name: string }) => Promise<void>;
  } = $props();

  let email = $state('');
  let password = $state('');
  let display_name = $state('');
  let error = $state('');
  let busy = $state(false);

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    error = '';
    busy = true;
    try {
      await onsubmit({ email, password, display_name });
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      busy = false;
    }
  }
</script>

<form class="narrow" onsubmit={submit} novalidate>
  <div class="top"><LanguageSwitch /></div>
  <h1>{mode === 'login' ? t.auth.signIn : t.auth.register}</h1>
  <div class="field">
    <label for="email">{t.auth.email}</label>
    <input id="email" type="email" autocomplete="email" required bind:value={email} />
  </div>
  {#if mode === 'register'}
    <div class="field">
      <label for="display_name">{t.auth.displayName}</label>
      <input id="display_name" type="text" autocomplete="name" bind:value={display_name} />
    </div>
  {/if}
  <div class="field">
    <label for="password">{t.auth.password}</label>
    <input
      id="password"
      type="password"
      autocomplete={mode === 'login' ? 'current-password' : 'new-password'}
      required
      minlength="8"
      bind:value={password}
    />
  </div>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit" disabled={busy}>
    {busy ? t.auth.working : mode === 'login' ? t.auth.signIn : t.auth.register}
  </button>
  <p class="switch">
    {#if mode === 'login'}
      {t.auth.noAccount} <a href="/register">{t.auth.register}</a>
    {:else}
      {t.auth.haveAccount} <a href="/login">{t.auth.signIn}</a>
    {/if}
  </p>
</form>

<style>
  .top {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.5rem;
  }
  .switch {
    margin: 1rem 0 0;
    font-size: 0.9rem;
    color: var(--ink-muted);
  }
</style>
