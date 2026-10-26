import client from './client';

export interface ImportResult {
  created: number;
  updated: number;
  skipped: number;
  errors: string[];
}

export async function importPublicData(kind: 'jobs' | 'resumes'): Promise<ImportResult> {
  return (await client.post<ImportResult>(`/imports/${kind}`)).data;
}
