/**
 * Tests for {@link parseIntWithCheck}.
 */

import { describe, expect, it } from 'vite-plus/test';

import { parseIntWithCheck } from './parseIntWithCheck';

describe('parseIntWithCheck', () => {
  it('parses numeric strings and numbers', () => {
    expect(parseIntWithCheck('42')).toBe(42);
    expect(parseIntWithCheck(7)).toBe(7);
  });

  it('returns the default value for missing or non-numeric input', () => {
    expect(parseIntWithCheck(null)).toBe(0);
    expect(parseIntWithCheck(undefined, { defaultValue: 5 })).toBe(5);
    expect(parseIntWithCheck('abc', { defaultValue: 1 })).toBe(1);
  });

  it('returns the default value when below the minimum', () => {
    expect(parseIntWithCheck('-3')).toBe(0);
    expect(parseIntWithCheck('2', { min: 3, defaultValue: 10 })).toBe(10);
    expect(parseIntWithCheck('3', { min: 3, defaultValue: 10 })).toBe(3);
  });
});
