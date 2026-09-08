// Language selection without a library (SPEC §8). The choice lives in
// localStorage; switching reloads the page so every module-level import of
// `t` sees the same strings. Simple, and the whole app is small enough for it.
import { en, type Strings } from './en';
import { tr } from './tr';

export type Language = 'en' | 'tr';
export const languages: Language[] = ['en', 'tr'];

function stored(): Language {
  try {
    const value = localStorage.getItem('charter.lang');
    if (value === 'tr' || value === 'en') return value;
    return navigator.language.toLowerCase().startsWith('tr') ? 'tr' : 'en';
  } catch {
    return 'en';
  }
}

export const language: Language = typeof window === 'undefined' ? 'en' : stored();
export const t: Strings = language === 'tr' ? tr : en;

if (typeof document !== 'undefined') document.documentElement.lang = language;

export function setLanguage(next: Language): void {
  try {
    localStorage.setItem('charter.lang', next);
  } catch {
    /* private mode: the choice just does not persist */
  }
  location.reload();
}
