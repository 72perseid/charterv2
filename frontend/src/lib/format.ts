import { language } from '$lib/i18n';

const locale = language === 'tr' ? 'tr-TR' : 'en-GB';

const dateFormat = new Intl.DateTimeFormat(locale, {
  year: 'numeric',
  month: 'short',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
});

export function formatDate(iso: string): string {
  return dateFormat.format(new Date(iso));
}

export function formatInt(n: number): string {
  return new Intl.NumberFormat(locale).format(n);
}

/** A statistic for reading, not for computing: six significant digits, no float noise. */
export function formatStat(value: unknown): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return String(value ?? '');
  return Number.isInteger(value) ? String(value) : String(Number(value.toPrecision(6)));
}
