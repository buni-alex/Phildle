import { fetchPhilosophersNames } from '../services/data_service'

export async function getPhilosophers(): Promise<string[]> {
  const cached = sessionStorage.getItem("philosophers")

  if (!cached) {
    const names = await fetchPhilosophersNames()
    sessionStorage.setItem("philosophers", JSON.stringify(names))
    return names
  } else {
    return JSON.parse(cached)
  }
}

export function clearPhilosophersCache() {
  sessionStorage.removeItem("philosophers")
}