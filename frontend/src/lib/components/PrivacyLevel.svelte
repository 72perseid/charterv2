<script lang="ts">
  import type { PrivacyLevel } from '$lib/api';
  import { t } from '$lib/i18n/en';

  let {
    value,
    onchange,
    disabled = false
  }: { value: PrivacyLevel; onchange: (level: PrivacyLevel) => void; disabled?: boolean } =
    $props();

  const levels: PrivacyLevel[] = ['minimal', 'statistics', 'sample'];
</script>

<fieldset class="privacy" {disabled}>
  <legend>{t.datasets.privacy.label}</legend>
  {#each levels as level (level)}
    <label class="option" class:chosen={level === value}>
      <input type="radio" name="privacy" value={level} checked={level === value} onchange={() => onchange(level)} />
      <span class="name">{t.datasets.privacy.levels[level]}</span>
      <span class="desc">{t.datasets.privacy.describe[level]}</span>
    </label>
  {/each}
</fieldset>

<style>
  .privacy {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.75rem 1rem 0.5rem;
    margin: 0;
    background: var(--surface);
  }
  legend {
    font-size: 0.85rem;
    color: var(--ink-muted);
    padding: 0 0.3rem;
  }
  .option {
    display: grid;
    grid-template-columns: auto auto 1fr;
    gap: 0.5rem;
    align-items: baseline;
    color: var(--ink);
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
    cursor: pointer;
  }
  .option input {
    width: auto;
  }
  .desc {
    color: var(--ink-muted);
    font-size: 0.85rem;
  }
  .chosen .name {
    font-weight: 600;
  }
</style>
