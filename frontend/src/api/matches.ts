import client from './client';
import type { MatchAnalyzeRequest, MatchReportListItem, MatchReportResponse } from '../types';

export async function analyzeMatch(data: MatchAnalyzeRequest): Promise<MatchReportResponse[]> {
  const res = await client.post<MatchReportResponse[]>('/matches/analyze', data);
  return res.data;
}

export async function listMatches(): Promise<MatchReportListItem[]> {
  const res = await client.get<MatchReportListItem[]>('/matches/');
  return res.data;
}

export async function getMatch(id: string): Promise<MatchReportResponse> {
  const res = await client.get<MatchReportResponse>(`/matches/${id}`);
  return res.data;
}
