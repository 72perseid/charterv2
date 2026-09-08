<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { ApiError, auth, modelConfig, type ModelTest } from '$lib/api';
  import { t } from '$lib/i18n/en';
  import { session } from '$lib/session.svelte';

  let { data } = $props();
  const s = t.settings;

  // The form holds a draft seeded from the saved config; after a save the two agree.
  // svelte-ignore state_referenced_locally
  let base_url = $state(data.config.base_url);
  // svelte-ignore state_referenced_locally
  let model = $state(data.config.model);
  let api_key = $state('');
  // svelte-ignore state_referenced_locally
  let temperature = $state(data.config.temperature);
  let error = $state('');
  let notice = $state('');
  let busy = $state(false);
  let testing = $state(false);
  let result: ModelTest | null = $state(null);
  let models: string[] = $state([]);
  let loadingModels = $state(false);
  let modelsFor = $state(''); // base URL the current list belongs to

  const canLoad = $derived(base_url.trim().length > 8 && (api_key !== '' || data.config.has_key));
  const listed = $derived(models.length > 0 && modelsFor === base_url.trim());
  const modelInList = $derived(listed && models.includes(model));

  async function loadModels() {
    if (!canLoad) return;
    error = '';
    loadingModels = true;
    try {
      models = (await modelConfig.models(base_url.trim(), api_key)).models;
      modelsFor = base_url.trim();
      if (models.length && (model === '' || !models.includes(model))) model = models[0];
    } catch (e) {
      models = [];
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      loadingModels = false;
    }
  }

  // Load once the URL and key are both in place, and again if the URL changes.
  function maybeLoad() {
    if (canLoad && modelsFor !== base_url.trim() && !loadingModels) loadModels();
  }

  const dirty = $derived(
    base_url !== data.config.base_url ||
      model !== data.config.model ||
      temperature !== data.config.temperature ||
      api_key !== ''
  );

  async function save(event: SubmitEvent) {
    event.preventDefault();
    error = notice = '';
    result = null;
    busy = true;
    try {
      await modelConfig.put({ base_url, model, api_key, temperature });
      api_key = '';
      notice = s.model.saved;
      await invalidateAll();
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      busy = false;
    }
  }

  async function test() {
    error = notice = '';
    testing = true;
    try {
      result = await modelConfig.test();
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      testing = false;
    }
  }

  async function signOut() {
    await auth.logout();
    session.set(null);
    await goto('/login');
  }
</script>

<svelte:head><title>{s.title} · {t.appName}</title></svelte:head>

<h1>{s.title}</h1>

<section class="card">
  <h2>{s.model.title}</h2>
  <p class="lead">{s.model.lead}</p>

  <form onsubmit={save}>
    <div class="field">
      <label for="base_url">{s.model.baseUrl}</label>
      <input id="base_url" type="url" required bind:value={base_url} placeholder="https://…/v1" onblur={maybeLoad} />
      <small>{s.model.baseUrlHint}</small>
    </div>
    <div class="field">
      <label for="api_key">{s.model.apiKey}</label>
      <input
        id="api_key"
        type="password"
        autocomplete="off"
        bind:value={api_key}
        required={!data.config.has_key}
        onblur={maybeLoad}
      />
      <small>
        {data.config.has_key
          ? s.model.apiKeyKeep.replace('{hint}', data.config.key_hint)
          : s.model.apiKeyNew}
      </small>
    </div>
    <div class="field">
      <label for="model">{s.model.model}</label>
      <div class="model-row">
        {#if listed}
          <select id="model" value={modelInList ? model : '__other__'} onchange={(e) => { const v = e.currentTarget.value; model = v === '__other__' ? '' : v; }}>
            {#each models as m (m)}
              <option value={m}>{m}</option>
            {/each}
            <option value="__other__">{s.model.otherModel}</option>
          </select>
          {#if !modelInList}
            <input type="text" required bind:value={model} aria-label={s.model.model} />
          {/if}
        {:else}
          <input id="model" type="text" required bind:value={model} />
        {/if}
        <button type="button" class="quiet" onclick={loadModels} disabled={!canLoad || loadingModels}>
          {loadingModels ? s.model.loadingModels : s.model.loadModels}
        </button>
      </div>
      <small>
        {#if listed}
          {s.model.modelsLoaded.replace('{n}', String(models.length))}
        {:else if canLoad}
          {s.model.modelHint}
        {:else}
          {s.model.modelsNeedKey}
        {/if}
      </small>
    </div>
    <div class="field narrow-field">
      <label for="temperature">{s.model.temperature}</label>
      <input id="temperature" type="number" min="0" max="2" step="0.1" bind:value={temperature} />
      <small>{s.model.temperatureHint}</small>
    </div>

    {#if error}<p class="error" role="alert">{error}</p>{/if}
    {#if notice}<p class="notice" role="status">{notice}</p>{/if}

    <div class="actions">
      <button type="submit" disabled={busy || !dirty}>{s.model.save}</button>
      <button
        type="button"
        class="quiet"
        onclick={test}
        disabled={testing || !data.config.has_key || dirty}
        title={dirty ? s.model.unsaved : ''}
      >
        {testing ? s.model.testing : s.model.test}
      </button>
      {#if result}
        <span class="result" class:ok={result.ok} class:bad={!result.ok} role="status">
          <span class="dot" aria-hidden="true"></span>
          <strong>{result.ok ? s.model.connected : s.model.notConnected}</strong>
          <span class="detail">
            {result.message}
            {#if result.ok && result.duration_ms !== null}· {result.model} · {result.duration_ms} ms{/if}
          </span>
        </span>
      {/if}
    </div>
  </form>
</section>

<section class="card">
  <h2>{s.account.title}</h2>
  <dl>
    <dt>{s.account.email}</dt>
    <dd>{session.user?.email}</dd>
    <dt>{s.account.name}</dt>
    <dd>{session.user?.display_name || '—'}</dd>
  </dl>
  <button type="button" class="quiet" onclick={signOut}>{s.account.signOut}</button>
</section>

<style>
  .card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    max-width: 40rem;
  }
  .lead {
    color: var(--ink-muted);
    font-size: 0.95rem;
  }
  .field small {
    display: block;
    color: var(--ink-muted);
    font-size: 0.8rem;
    margin-top: 0.25rem;
  }
  .narrow-field input {
    max-width: 8rem;
  }
  .model-row {
    display: flex;
    gap: 0.5rem;
    align-items: stretch;
  }
  .model-row select,
  .model-row input {
    flex: 1;
    min-width: 0;
  }
  .model-row button {
    white-space: nowrap;
  }
  .notice {
    color: var(--success);
    margin: 0.5rem 0 1rem;
  }
  .actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  .result {
    display: inline-flex;
    align-items: baseline;
    gap: 0.5rem;
    padding: 0.3rem 0.7rem;
    border-radius: var(--radius);
    border: 1px solid var(--line);
    font-size: 0.9rem;
  }
  .result .dot {
    width: 0.6rem;
    height: 0.6rem;
    border-radius: 50%;
    align-self: center;
  }
  .result.ok {
    border-color: var(--success);
  }
  .result.ok .dot {
    background: var(--success);
  }
  .result.bad {
    border-color: var(--destructive);
  }
  .result.bad .dot {
    background: var(--destructive);
  }
  .detail {
    color: var(--ink-muted);
  }
  dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.4rem 1.5rem;
    margin: 0 0 1rem;
  }
  dt {
    color: var(--ink-muted);
  }
  dd {
    margin: 0;
  }
</style>
