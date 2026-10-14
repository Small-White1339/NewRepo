import client from './client';
import type { ResumeListItem, ResumeResponse, ResumeUpdateRequest, ResumeUploadResponse } from '../types';

export async function uploadResume(file: File): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await client.post<ResumeUploadResponse>('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function listResumes(params?: { q?: string; status?: string }): Promise<ResumeListItem[]> {
  const res = await client.get<ResumeListItem[]>('/resumes/', { params });
  return res.data;
}

export async function getResume(id: string): Promise<ResumeResponse> {
  const res = await client.get<ResumeResponse>(`/resumes/${id}`);
  return res.data;
}

export async function updateResume(id: string, data: ResumeUpdateRequest): Promise<ResumeResponse> {
  const res = await client.put<ResumeResponse>(`/resumes/${id}`, data);
  return res.data;
}

export async function deleteResume(id: string): Promise<void> {
  await client.delete(`/resumes/${id}`);
}

export async function analyzeResume(id: string): Promise<ResumeResponse> {
  const res = await client.post<ResumeResponse>(`/resumes/${id}/analyze`);
  return res.data;
}
