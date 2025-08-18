export type DailyPhildle = {
  phildle_id: number;
  date: string;
  quote_text: string;
  philosopher_name: string;
  school: string;
  country: string;
  birth_date: string;
  death_date: string | null;
  daily_replay: { daily_success: boolean, attempts: number } | null;
};