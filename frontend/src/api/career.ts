import client from './client';
import type { JobListItem, MatchAnalysisResult, MatchStatus } from '../types';

export interface CareerJob extends JobListItem { raw_description?: string | null }
export type CareerStage = 'SAVED' | 'APPLIED' | 'INTERVIEW' | 'OFFER' | 'ARCHIVED';
export const careerStages: Record<CareerStage, string> = {
  SAVED: '已收藏', APPLIED: '已投递', INTERVIEW: '面试中', OFFER: '收到录用', ARCHIVED: '已归档',
};
export interface SavedJob {
  job: CareerJob; stage: CareerStage; notes: string; updated_at: string;
}
export interface CareerReport {
  id: string; resume_id: string; job_id: string; status: MatchStatus; overall_score?: number | null;
  job_title: string; company: string; resume_title: string; created_at: string;
  result_data?: {
    error?: string;
    match_result?: MatchAnalysisResult;
    report?: { summary: string; resume_tips: string[]; learning_plan: string[]; interview_preparation: string[] };
  };
}
export const browseCareerJobs = async (params?: { q?: string; level?: string }) =>
  (await client.get<CareerJob[]>('/career/jobs', { params })).data;
export const getCareerJob = async (id: string) =>
  (await client.get<CareerJob>(`/career/jobs/${id}`)).data;
export const listSavedJobs = async () => (await client.get<SavedJob[]>('/career/saved')).data;
export const saveCareerJob = async (id: string, stage: CareerStage = 'SAVED', notes = '') =>
  (await client.put<SavedJob>(`/career/saved/${id}`, { stage, notes })).data;
export const removeSavedJob = async (id: string) => { await client.delete(`/career/saved/${id}`); };
export const analyzeCareerMatch = async (job_id: string, resume_id: string) =>
  (await client.post<CareerReport>('/career/analyze', { job_id, resume_id })).data;
export const listCareerReports = async () => (await client.get<CareerReport[]>('/career/reports')).data;
