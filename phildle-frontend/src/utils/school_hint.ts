export function getSchoolHint(guessRaw: string | null, correctRaw: string | null) {
  if (!guessRaw || !correctRaw) {
    return {
      matches: [],
      allCorrectMatched: false,
    };
  }

  const guessSchools = guessRaw.split(",").map(s => s.trim()).filter(Boolean);
  const correctSchools = correctRaw.split(",").map(s => s.trim()).filter(Boolean);

  const correctSetLower = new Set(correctSchools.map(s => s.toLowerCase()));
  let unmatchedCount = correctSetLower.size;

  const matches: ("true" | "maybe" | "false")[] = [];
 
  for (const school of guessSchools) {
    const lower = school.toLowerCase();

    if (correctSetLower.has(lower)) {
      // Exact match
      matches.push("true");
      --unmatchedCount;
      continue;
    }

    // Check for "maybe" match: any token in guess is substring of any correct school or vice versa
    // Only consider tokens > 4 letters for fuzziness
    const tokens = school.split(/\s+/).filter(t => t.length > 4);
    let maybeFound = false;
    let skipSet = new Set(['philosophy', 'late', 'modern'])

    outer: for (const token of tokens) {
      if (skipSet.has(token))
        continue;
      for (const correctSchool of correctSchools) {
        const correctLower = correctSchool.toLowerCase();
        if (correctLower.includes(token) || token.includes(correctLower)) {
          maybeFound = true;
          break outer;
        }
      }
    }

    if (maybeFound) {
      matches.push("maybe");
    } else {
      matches.push("false");
    }
  }

  const allCorrectMatched = unmatchedCount === 0;

  return { matches, allCorrectMatched };
}