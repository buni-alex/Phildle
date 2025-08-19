import type { UserStats } from '../types/user';
const API_BASE = "/api/history";


export async function initUser(): Promise<{ user_uuid: string; new_user: boolean }> {
  const resp = await fetch(`${API_BASE}/init_user`, { credentials: "include" })
  if (!resp.ok) throw new Error(`Failed to init user: ${resp.statusText}`)
  const data = await resp.json() as { user_uuid: string; new_user: boolean }
  return data
}

export async function recordPlay(
  phildleId: number,
  attempts: number | null,
  success: boolean
): Promise<{ current_streak: number; max_streak: number }> {
  // Force attempts to null if unsuccessful
  const safeAttempts = success ? attempts : null;

  const resp = await fetch(`${API_BASE}/record_play`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      phildle_id: phildleId,
      attempts: safeAttempts,
      success
    }),
  });

  return await resp.json(); // returns streaks directly
}

export async function fetchHistory() {
    const resp = await fetch(`${API_BASE}`, { credentials: 'include' })
    return await resp.json();
}

export async function fetchUserStats(): Promise<UserStats> {
  const response = await fetch(`${API_BASE}/user_stats`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch user stats: ${response.statusText}`);
  }

  const data: UserStats = await response.json();
  return data;
}