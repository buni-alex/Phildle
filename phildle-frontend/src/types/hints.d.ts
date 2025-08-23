export type Hints = {
  nameHint: boolean;
  countryHint: {
    canonicalCorrect: boolean,
    fullyCorrect: boolean
  } | null;
  schoolHint: {
    matches: string[],
    allCorrectMatched: boolean
  } | null;
  birthDateHint: string | null;
  deathDateHint: string | null;
}