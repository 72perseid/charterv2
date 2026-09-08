// The only place the browser talks to the server. Plain fetch, same-origin,
// session cookie plus CSRF header. No client cache library (SPEC §8).
import { t } from '$lib/i18n/en';

export class ApiError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

export type User = { id: string; email: string; display_name: string };

export type Dataset = {
  id: number;
  name: string;
  original_filename: string;
  row_count: number;
  column_count: number;
  size_bytes: number;
  privacy_level: 'minimal' | 'statistics' | 'sample';
  status: 'pending' | 'running' | 'done' | 'failed';
  error_message: string | null;
  created_at: string;
};

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

export const datasets = {
  list: () => request<Dataset[]>('/datasets')
};
