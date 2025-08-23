export type Philosopher = {
  id: number;
  name: string;
  school: string;
  country: string;
  birth_date: string;
  death_date: string | null;
  info: string | null;
  wiki_image_url: string | null;
  wiki_image_meta: Record<string, any> | null;
}