import type { DailyPhildle } from '../types/daily_phildle'
import type { Philosopher } from '../types/philosopher'

export async function fetchDailyPhildle(): Promise<DailyPhildle> {
  const response = await fetch('/api/today')
  if (!response.ok) throw new Error('Failed to fetch daily Phildle')
  const data = await response.json()
  console.log(data)
  return data
}

export async function fetchPhildleById(id : number): Promise<DailyPhildle> {
  const encodedId = encodeURIComponent(id)
  const response = await fetch(`/api/phildle/by_id/${encodedId}`)
  if (!response.ok) throw new Error(`Error fetching phildle: ${response.statusText}`)
  return await response.json()
}

export async function fetchPhilosophersNames(): Promise<string[]> {
  const response = await fetch('/api/philosophers/all_names')
  if (!response.ok) throw new Error('Failed to fetch philosophers')
  return await response.json()
}

export async function fetchPhilosopher(name: string) : Promise<Philosopher> {
  const encodedName = encodeURIComponent(name)
  const response = await fetch(`/api/philosophers/by_name/${encodedName}`)
  if (!response.ok) throw new Error(`Error fetching philosopher: ${response.statusText}`)
  return await response.json()
}