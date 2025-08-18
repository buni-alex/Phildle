export type Hints = {
  countryHint: {
    canonicalCorrect: boolean,
    fullyCorrect: boolean
  };
  schoolHint: {
    matches: string[],
    allCorrectMatched: boolean
  };
  birthDateHint: string;
  deathDateHint: string;
}