/**
 * Turns what a person typed into a +E.164-style number, or null if it can't be one.
 * Numbers without "+" get DEFAULT_COUNTRY_CODE when they have 10 digits.
 */
export function normalizePhone(input: string, defaultCc = "1"): string | null {
  const trimmed = input.trim();
  const digits = trimmed.replace(/\D/g, "");
  if (trimmed.startsWith("+")) {
    return digits.length >= 8 && digits.length <= 15 ? `+${digits}` : null;
  }
  if (digits.length === 10) return `+${defaultCc}${digits}`;
  if (digits.length === 11 && digits.startsWith(defaultCc)) return `+${digits}`;
  return null;
}

/** Friendly display, e.g. +18005550199 -> +1 800 555 0199 */
export function prettyPhone(e164: string): string {
  const m = e164.match(/^\+1(\d{3})(\d{3})(\d{4})$/);
  return m ? `+1 ${m[1]} ${m[2]} ${m[3]}` : e164;
}
