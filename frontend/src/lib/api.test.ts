import { describe, expect, it } from 'vitest';
import { detailOf } from './api';
import { t } from './i18n/en';

describe('detailOf', () => {
  it('returns a plain detail string', () => {
    expect(detailOf({ detail: 'Email or password is incorrect.' })).toBe(
      'Email or password is incorrect.'
    );
  });
  it('joins ninja validation messages', () => {
    expect(
      detailOf({
        detail: [
          { loc: ['body', 'data', 'email'], msg: 'Value error, Enter a valid email address.' },
          { loc: ['body', 'data', 'password'], msg: 'String should have at least 8 characters' }
        ]
      })
    ).toContain('at least 8 characters');
  });
  it('falls back to the generic message', () => {
    expect(detailOf(null)).toBe(t.errors.unknown);
    expect(detailOf('<html>')).toBe(t.errors.unknown);
  });
});
