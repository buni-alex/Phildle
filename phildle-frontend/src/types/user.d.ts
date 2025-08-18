export type UserPlay = {
  past_phildle_id: number;
  attempts: number;
  success: boolean;
  played_on: string;
}

export type UserStats = {
  current_streak: number;
  max_streak: number;
  attempt_distribution: Record<number, number>;
  losses: number;
  total_played: number
}