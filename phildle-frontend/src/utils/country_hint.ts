import { COUNTRY_EQUIVALENCE } from './country_equivalences'

/**
 * Cleans a country string by:
 * 1. Removing parenthetical content.
 * 2. Splitting by commas and taking the last part.
 * 3. Trimming and extracting the last word.
 */
export function extractCountryName(raw: string): string {
  // Remove parentheses and their contents
  const noParens = raw.replace(/\s*\(.*?\)\s*/g, '');

  // Split by comma and take the last chunk
  const parts = noParens.split(',');
  // Find the last non-empty part from the end
  for (let i = parts.length - 1; i >= 0; i--) {
    if (parts[i]) {
      return parts[i].trim();
    }
  }
  return ''
}

/**
 * Maps a cleaned country name to its canonical country from COUNTRY_EQUIVALENCE.
 */
export function mapToCanonicalCountry(country: string): string | null {
  for (const [canonical, equivalents] of Object.entries(COUNTRY_EQUIVALENCE)) {
    if (equivalents.has(country)) return canonical;
  }
  return country;  // fallback to returning the input itself
}

/**
 * Compares guessed country to correct one, accounting for historical/alternate forms.
 */
export function getCountryHint(guessedRaw: string, correctRaw: string) : {canonicalCorrect: boolean, fullyCorrect: boolean} {
  const guessed = extractCountryName(guessedRaw);
  const correct = extractCountryName(correctRaw);

  const guessedMapped = mapToCanonicalCountry(guessed);
  const correctMapped = mapToCanonicalCountry(correct);

  return {
    canonicalCorrect: guessedMapped !== null && correctMapped !== null && guessedMapped === correctMapped,
    fullyCorrect: guessed === correct
  }
}