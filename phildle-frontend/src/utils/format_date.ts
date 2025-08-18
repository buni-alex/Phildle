export function formatDate(dateString: string) {
  if (!dateString) return ''
  // Only reformat if it matches full YYYY-MM-DD
  const match = dateString.match(/^(\d{1,4})-(\d{2})-(\d{2})$/)
  if (!match) return dateString // keep as-is if it's something else
  let [, year, month, day] = match
  year = String(Number(year)) // <-- removes leading zeros
  return `${day}.${month}.${year}`
}