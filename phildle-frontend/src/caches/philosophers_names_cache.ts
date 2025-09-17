import { fetchPhilosophersNames } from '../services/data_service'

export async function getPhilosophersNames(): Promise<string[]> {
  const cached = sessionStorage.getItem("philosophersNames")

  if (!cached) {
    const names = await fetchPhilosophersNames()
    sessionStorage.setItem("philosophersNames", JSON.stringify(names))
    return names
  } else {
    return JSON.parse(cached)
  }
}

export function clearPhilosophersCache() {
  sessionStorage.removeItem("philosophers")
}