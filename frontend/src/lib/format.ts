const dateFormat = new Intl.DateTimeFormat('en-GB', {
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
  return new Intl.NumberFormat('en-GB').format(n);
}
