// The only place the browser talks to the server. Plain fetch, same-origin,
// session cookie plus CSRF header. No client cache library (SPEC §8).
import { t } from '$lib/i18n';

export class ApiError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

export type User = { id: string; email: string; display_name: string };

export type Status = 'pending' | 'running' | 'done' | 'failed';
export type PrivacyLevel = 'minimal' | 'statistics' | 'sample';
export type ColumnType = 'integer' | 'number' | 'date' | 'boolean' | 'string' | 'period';

// What the user says about one text column: a list is the chronological order
// (oldest first), true makes it a period column with the detected order, false
// keeps it plain text, null hands it back to detection.
export type PeriodChoice = string[] | boolean | null;

export type Dataset = {
  id: number;
  name: string;
  original_filename: string;
  row_count: number;
  column_count: number;
  size_bytes: number;
  privacy_level: PrivacyLevel;
  status: Status;
  error_message: string | null;
  created_at: string;
};

export type ColumnProfile = {
  name: string;
  original_name: string;
  type: ColumnType;
  null_count: number;
  distinct_count: number;
  min?: number | string;
  max?: number | string;
  mean?: number;
  median?: number;
  true_count?: number;
  top_values?: { value: string; count: number }[];
  max_length?: number;
  // period columns: every distinct value oldest first; `unplaced` sort last
  order?: string[];
  unplaced?: string[];
  order_source?: 'detected' | 'user';
  // which PeriodO definition (or date) decided each value's place, and for where
  matches?: PeriodMatch[];
  region?: string | null;
  periodo_snapshot?: string;
  // the columns of this dataset that date the values, when the user linked them
  dated_by?: PeriodDates;
};

// Start and end year columns for a period column; `bc` when years are counted backwards.
export type PeriodDates = { start: string; end?: string | null; bc?: boolean };

export type PeriodMatch = {
  value: string;
  start: number;
  stop: number;
  via: 'periodo' | 'abbreviation' | 'translation' | 'derived' | 'year' | 'model' | 'user' | 'data';
  label?: string;
  id?: string; // PeriodO id; PERIODO_PERMALINK + id opens the definition
  source?: string;
  varies?: boolean; // via data: the rows with this value do not all give the same dates
};

export const PERIODO_PERMALINK = 'http://n2t.net/ark:/99152/';

// The stored record of one "ask the model" call for a period column.
export type PeriodRequest = {
  asked_at: string;
  labels: string[];
  answered?: string[];
  error?: string;
  model?: string;
  endpoint_host?: string;
};

export type ParseOptions = {
  kind?: 'text' | 'excel';
  encoding?: string;
  delimiter?: string;
  decimal?: string;
  sheet?: string;
  sheets?: string[];
  header_row?: number;
  overrides?: {
    sheet?: string;
    header_row?: number;
    periods?: Record<string, string[] | boolean>;
    // per column, per value: what the user says the value means
    period_mappings?: Record<string, Record<string, string>>;
    period_dates?: Record<string, PeriodDates>;
  };
  period_requests?: Record<string, PeriodRequest>;
};

export type DatasetDetail = Dataset & {
  sheet_name: string | null;
  parse_options: ParseOptions;
  profile: { row_count?: number; column_count?: number; columns?: ColumnProfile[] };
};

export type Cell = string | number | boolean | null;

export type Rows = {
  total: number;
  offset: number;
  limit: number;
  columns: string[];
  rows: Record<string, Cell>[];
};

export function isBusy(status: Status): boolean {
  return status === 'pending' || status === 'running';
}

function readCookie(name: string): string {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : '';
}

let csrfReady: Promise<void> | null = null;

function ensureCsrf(): Promise<void> {
  if (!csrfReady) {
    csrfReady = fetch('/api/auth/csrf', { credentials: 'same-origin' }).then(() => undefined);
  }
  return csrfReady;
}

export async function request<T>(
  path: string,
  init: { method?: string; body?: unknown } = {}
): Promise<T> {
  const method = init.method ?? 'GET';
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (method !== 'GET') {
    await ensureCsrf();
    headers['X-CSRFToken'] = readCookie('csrftoken');
  }
  let body: BodyInit | undefined;
  if (init.body instanceof FormData) {
    body = init.body;
  } else if (init.body !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(init.body);
  }

  let response: Response;
  try {
    response = await fetch('/api' + path, { method, headers, body, credentials: 'same-origin' });
  } catch {
    throw new ApiError(0, t.errors.network);
  }

  if (response.status === 204) return undefined as T;
  const text = await response.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!response.ok) {
    throw new ApiError(response.status, detailOf(data));
  }
  return data as T;
}

export function detailOf(data: unknown): string {
  if (data && typeof data === 'object' && 'detail' in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === 'string') return detail;
    // django-ninja validation errors: [{loc, msg, ...}]
    if (Array.isArray(detail)) {
      return detail
        .map((d) => (d && typeof d === 'object' && 'msg' in d ? String(d.msg) : ''))
        .filter(Boolean)
        .join(' ');
    }
  }
  return t.errors.unknown;
}

export const auth = {
  me: () => request<User>('/auth/me'),
  register: (email: string, password: string, display_name: string) =>
    request<User>('/auth/register', { method: 'POST', body: { email, password, display_name } }),
  login: (email: string, password: string) =>
    request<User>('/auth/login', { method: 'POST', body: { email, password } }),
  logout: () => request<void>('/auth/logout', { method: 'POST' })
};

export type ModelConfig = {
  base_url: string;
  model: string;
  temperature: number;
  has_key: boolean;
  key_hint: string;
  key_optional: boolean; // this server allows local endpoints, which need no key
  input_price_per_million: number | null;
  output_price_per_million: number | null;
  updated_at: string | null;
};

export type ModelPrice = { input_per_million: number; output_per_million: number };

export type ModelTest = {
  ok: boolean;
  message: string;
  model: string | null;
  duration_ms: number | null;
};

export const modelConfig = {
  get: () => request<ModelConfig>('/me/model-config'),
  put: (fields: {
    base_url: string;
    model: string;
    api_key: string;
    temperature: number;
    input_price_per_million: number | null;
    output_price_per_million: number | null;
  }) => request<ModelConfig>('/me/model-config', { method: 'PUT', body: fields }),
  test: () => request<ModelTest>('/me/model-config/test', { method: 'POST' }),
  models: (base_url: string, api_key: string) =>
    request<{ models: string[]; pricing: Record<string, ModelPrice> }>('/me/model-config/models', {
      method: 'POST',
      body: { base_url, api_key }
    })
};

export type RevisionSummary = {
  id: number;
  revision_no: number;
  parent_id: number | null;
  x_field: string;
  y_field: string;
  color_field: string | null;
  prompt: string;
  status: Status;
  error_message: string | null;
  model: string;
  duration_ms: number | null;
  cost_usd: number | null;
  created_at: string;
};

export type Revision = RevisionSummary & {
  chart_id: number;
  attempts: number;
  spec: Record<string, unknown> | null;
  corrections: string[];
  request: {
    attempt: number;
    messages: { role: string; content: string }[];
    parameters: Record<string, unknown>;
    adjustments: string[];
    pricing?: { input_per_million: number | null; output_per_million: number | null };
  } | null;
  cost_at_current_prices: number | null;
  response_text: string | null;
  endpoint_host: string;
  temperature: number | null;
  seed: number | null;
  prompt_version: string;
  app_version: string;
  usage: Record<string, number> | null;
  started_at: string | null;
  finished_at: string | null;
};

export type Chart = {
  id: number;
  dataset_id: number;
  dataset_name: string;
  title: string;
  current_revision_id: number | null;
  current_status: Status | null;
  revision_count: number;
  created_at: string;
  updated_at: string;
};

export type ChartDetail = Chart & { revisions: RevisionSummary[] };

export type RevisionFields = {
  x_field: string;
  y_field: string;
  color_field: string | null;
  prompt: string;
};

export const charts = {
  list: () => request<Chart[]>('/charts'),
  get: (id: number) => request<ChartDetail>(`/charts/${id}`),
  create: (fields: RevisionFields & { dataset_id: number; title: string }) =>
    request<ChartDetail>('/charts', { method: 'POST', body: fields }),
  patch: (id: number, fields: { title?: string; current_revision_id?: number }) =>
    request<ChartDetail>(`/charts/${id}`, { method: 'PATCH', body: fields }),
  remove: (id: number) => request<void>(`/charts/${id}`, { method: 'DELETE' }),
  revise: (id: number, fields: RevisionFields & { parent_id: number | null }) =>
    request<Revision>(`/charts/${id}/revisions`, { method: 'POST', body: fields }),
  exportUrl: (id: number) => `/api/charts/${id}/export`
};

export const revisions = {
  get: (id: number) => request<Revision>(`/revisions/${id}`)
};

export const datasets = {
  list: () => request<Dataset[]>('/datasets'),
  get: (id: number) => request<DatasetDetail>(`/datasets/${id}`),
  upload: (file: File, name: string) => {
    const body = new FormData();
    body.append('file', file);
    body.append('name', name);
    return request<DatasetDetail>('/datasets', { method: 'POST', body });
  },
  patch: (
    id: number,
    fields: {
      name?: string;
      privacy_level?: PrivacyLevel;
      sheet?: string;
      header_row?: number;
      periods?: Record<string, PeriodChoice>;
      period_mappings?: Record<string, Record<string, string | null>>;
      period_dates?: Record<string, PeriodDates | null>;
    }
  ) => request<DatasetDetail>(`/datasets/${id}`, { method: 'PATCH', body: fields }),
  // Sends the column's distinct values to the user's model: only ever on a click.
  askPeriods: (id: number, column: string) =>
    request<DatasetDetail>(`/datasets/${id}/periods/ask`, { method: 'POST', body: { column } }),
  remove: (id: number) => request<void>(`/datasets/${id}`, { method: 'DELETE' }),
  rows: (id: number, limit = 100, offset = 0) =>
    request<Rows>(`/datasets/${id}/rows?limit=${limit}&offset=${offset}`),
  downloadUrl: (id: number) => `/api/datasets/${id}/download`
};
