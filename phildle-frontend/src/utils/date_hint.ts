//import { fileURLToPath } from 'url';
function parseYearRange(dateStr: string | null): { min: number, max: number } | null {
  if (!dateStr) return null;

  const lower = dateStr.toLowerCase().trim();
  let cleaned = lower.replace(/[(),]/g, '').replace(/\s+/g, ' ');
  // Remove AD/CE and similar terms
  cleaned = cleaned
    .replace(/\b(ad|ce)\b/g, '')   // remove "ad", "ce" with word boundaries
    .replace(/\s+/g, ' ')          // collapse spaces again if any remain
    .trim();
  const isBC = cleaned.includes('bc') || cleaned.includes('bce');
  const numericPart = cleaned.replace(/[^0-9\/\-– ]/g, '');

  let years: number[] = [];

  // Slash-separated years: "428/427/423"
  if (numericPart.includes('/')) {
    years = numericPart
      .split('/')
      .map(s => parseInt(s.trim(), 10))
      .filter(n => !isNaN(n));
  }

  // Dash-range years: "20-30" or "428–423"
  else if (numericPart.includes('-') || numericPart.includes('–')) {
    const parts = numericPart.split(/[-–]/).map(s => parseInt(s.trim(), 10));
    if (parts.length === 2 && parts.every(n => !isNaN(n))) {
      years = [parts[0], parts[1]];
    }
  }

  // Century format: "5th century BC"
  const centuryMatch = cleaned.match(/(\d+)(?:st|nd|rd|th)? century/);
  if (centuryMatch) {
    const century = parseInt(centuryMatch[1], 10);
    const start = (century - 1) * 100;
    const end = start + 99;
    const min = isBC ? -end : start;
    const max = isBC ? -start : end;
    return { min, max };
  }

  // Regular year: "384", "1970-03-21"
  if (years.length === 0) {
    const match = cleaned.match(/(\d{1,4})/);
    if (match) {
      const year = parseInt(match[1], 10);
      if (!isNaN(year)) years = [year];
    }
  }

  if (years.length === 0) return null;

  let min = Math.min(...years);
  let max = Math.max(...years);
  if (isBC) {
    min = -Math.abs(max);
    max = -Math.abs(min);
    if (min > max) [min, max] = [max, min];
  }

  return { min, max };
}

function tryParseFullDate(dateStr: string | null): Date | null {
  if (!dateStr) return null;

  // Normalize and remove things like "BC", "AD", "CE", etc.
  const cleaned = dateStr
    .toLowerCase()
    .replace(/\b(bc|bce|ad|ce)\b/g, '')
    .replace(/[(),]/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  // Try formats like YYYY-MM-DD
  const isoMatch = cleaned.match(/\b(\d{3,4})[-\/](\d{1,2})[-\/](\d{1,2})\b/);
  if (isoMatch) {
    const [_, y, m, d] = isoMatch.map(Number);
    if (!isNaN(y) && !isNaN(m) && !isNaN(d)) {
      return new Date(y, m - 1, d);
    }
  }

  return null;
}

export function getDateHint(
  guessedRaw: string | null,
  correctRaw: string | null
): 'earlier' | 'later' | 'same' | 'maybe' | 'unknown' {
  const guessed = parseYearRange(guessedRaw);
  const correct = parseYearRange(correctRaw);

  console.log(guessed, correct)

  if(!guessed && correct) return 'earlier';
  else if(guessed && !correct) return 'unknown';
  else if (!guessed && !correct) return 'same';

  const guessedMin = guessed!.min;

  if (correct!.min === correct!.max) {
    if (guessed!.min > correct!.min) return 'earlier';
    if (guessed!.min < correct!.max) return 'later';

    // Years match exactly. Try parsing full dates:
    const guessedDate = tryParseFullDate(guessedRaw);
    const correctDate = tryParseFullDate(correctRaw);

    if (guessedDate && correctDate) {
      if (guessedDate.getTime() < correctDate.getTime()) return 'later';
      if (guessedDate.getTime() > correctDate.getTime()) return 'earlier';
      return 'same';
    }

    return 'same';
  } else {      // Correct is a range
    if (guessed!.min === correct!.min && guessed!.max === correct!.max)
      return "same";
    else if (guessed!.min >= correct!.min && guessedMin <= correct!.max)
      return 'maybe';
    else if (guessed!.min < correct!.min) 
      return 'later';
    else
      return 'earlier';
  }
}

//if (process.argv[1] === fileURLToPath(import.meta.url)) {
//  console.log(getDateHint("428", "428/427/424/423 BC")); // 'later'
//  console.log(getDateHint("427 BC", "428/427/424/423 BC")); // 'maybe'
//  console.log(getDateHint("5th century BC", "427 BC")); // 'same'
//  console.log(getDateHint("20", "20-30")); // 'maybe' (or your logic)
//  console.log(getDateHint("10", "20-30")); // 'earlier'
//  console.log(getDateHint("1940", "1940")); // 'same'
//  console.log(getDateHint("1940-01-14", "1940-03-21")) //earlier
//  console.log(getDateHint("1940-01-14", "1940-01-14")) //same
//  console.log(getDateHint("1950", null)); // 'unknown'
//}
