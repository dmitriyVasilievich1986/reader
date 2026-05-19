/**
 * Parses integers from user input strings with sane fallbacks when the value
 * is missing, non-numeric, or below an optional minimum threshold.
 */

/**
 * Parses `value` with `parseInt` (base 10 implicit).
 *
 * Returns `options.defaultValue` when the parse result is NaN or strictly
 * less than `options.min` (defaults preserve common pagination-style bounds).
 *
 * @param value - String to parse (e.g. query param).
 * @param options.defaultValue - Value used when parsing fails or is below `min`.
 * @param options.min - Inclusive minimum; values below yield `defaultValue`.
 * @returns The parsed integer or `defaultValue`.
 */
export const parseIntWithCheck = (
  value: string | null | undefined | number,
  options: { defaultValue?: number; min?: number } = {}
): number => {
  const { defaultValue = 0, min = 0 } = options;

  const parsed = parseInt(String(value));
  if (Number.isNaN(parsed) || parsed < min) {
    return defaultValue;
  }
  return parsed;
};
