import client from './client';
import type { JobCreateRequest, JobListItem, JobResponse, JobUpdateRequest } from '../types';

export async function createJob(data: JobCreateRequest): Promise<JobResponse> {
  const res = await client.post<JobResponse>('/jobs/', data);
  return res.data;
}

export async function listJobs(params?: { q?: string; status?: string; level?: string }): Promise<JobListItem[]> {
  const res = await client.get<JobListItem[]>('/jobs/', { params });
  return res.data;
}

export async function getJob(id: string): Promise<JobResponse> {
  const res = await client.get<JobResponse>(`/jobs/${id}`);
  return res.data;
}

export async function updateJob(id: string, data: JobUpdateRequest): Promise<JobResponse> {
  const res = await client.put<JobResponse>(`/jobs/${id}`, data);
  return res.data;
}

export async function analyzeJob(id: string): Promise<JobResponse> {
  const res = await client.post<JobResponse>(`/jobs/${id}/analyze`);
  return res.data;
}

export async function deleteJob(id: string): Promise<void> {
  await client.delete(`/jobs/${id}`);
}
