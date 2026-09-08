<script lang="ts">
  import { ApiError, datasets, type DatasetDetail } from '$lib/api';
  import { t } from '$lib/i18n';

  let {
    onuploaded,
    oncancel
  }: { onuploaded: (dataset: DatasetDetail) => void; oncancel: () => void } = $props();

  let file: File | null = $state(null);
  let name = $state('');
  let error = $state('');
  let busy = $state(false);

  function pick(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    file = input.files?.[0] ?? null;
    if (file && !name) name = file.name.replace(/\.[^.]+$/, '');
  }

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (!file) return;
    error = '';
    busy = true;
    try {
      onuploaded(await datasets.upload(file, name.trim()));
    } catch (e) {
      error = e instanceof ApiError ? e.message : t.errors.unknown;
    } finally {
      busy = false;
    }
  }
</script>

<form class="panel" onsubmit={submit}>
  <h2>{t.datasets.uploadForm.title}</h2>
  <div class="field">
    <label for="file">{t.datasets.uploadForm.file}</label>
    <input id="file" type="file" accept=".csv,.tsv,.txt,.xlsx" required onchange={pick} />
  </div>
  <div class="field">
    <label for="name">{t.datasets.uploadForm.name}</label>
    <input id="name" type="text" maxlength="200" bind:value={name} />
  </div>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <div class="actions">
    <button type="submit" disabled={busy || !file}>
      {busy ? t.datasets.uploadForm.uploading : t.datasets.uploadForm.submit}
    </button>
    <button type="button" class="quiet" onclick={oncancel} disabled={busy}>
      {t.datasets.uploadForm.cancel}
    </button>
  </div>
</form>

<style>
  .panel {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1.25rem;
    margin-bottom: 1.5rem;
    max-width: 32rem;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
  }
</style>
