import { fetchPhilosophersNames } from '../services/data_service'

let cachedPhilosophers: string[] | null = null

export async function getPhilosophers(): Promise<string[]> {
  if (!cachedPhilosophers) {
    cachedPhilosophers = await fetchPhilosophersNames()
  }
  return cachedPhilosophers
}

// Optional: clear cache if you ever need to refresh
export function clearPhilosophersCache() {
  cachedPhilosophers = null
}