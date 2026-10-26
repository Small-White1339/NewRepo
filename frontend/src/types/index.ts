// ── Auth ──
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserRegisterRequest {
  username: string;
  email: string;
  password: string;
  role: string;
}

export interface UserLoginRequest {
  username: string;
  password: string;
}

// ── Resume ──
export interface Education {
  id?: number;
  school: string;
  degree?: string;
  field?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

export interface Skill {
  id?: number;
  name: string;
  level?: string;
  category?: string;
}

export interface Project {
  id?: number;
  name: string;
  role?: string;
  description?: string;
  tech_stack?: string[];
  start_date?: string;
  end_date?: string;
  url?: string;
}

export interface WorkExperience {
  id?: number;
  company: string;
  title: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
}

export interface Certificate {
  id?: number;
  name: string;
  issuer?: string;
  issued_date?: string;
  url?: string;
}

export type ResumeStatus = 'PENDING' | 'PARSED' | 'FAILED';

export interface ResumeListItem {
  source_name?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  id: string;
  title: string;
  status: ResumeStatus;
  created_at: string;
}

export interface ResumeUploadResponse {
  id: string;
  title: string;
  status: ResumeStatus;
  message: string;
}

export interface ResumeUpdateRequest {
  title?: string;
}

export interface ResumeResponse {
  source_name?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  id: string;
  user_id: string;
  title: string;
  file_path: string;
  raw_text?: string;
  parsed_data?: Record<string, unknown>;
  status: ResumeStatus;
  created_at: string;
  updated_at: string;
  educations: Education[];
  skills: Skill[];
  projects: Project[];
  work_experiences: WorkExperience[];
  certificates: Certificate[];
}

// ── Job ──
export interface JobRequirement {
  id?: number;
  category: string;
  name: string;
  description?: string;
  importance: number;
  is_mandatory: boolean;
}

export type JobStatus = 'DRAFT' | 'ACTIVE' | 'CLOSED';
export type JobLevel = 'JUNIOR' | 'INTERMEDIATE' | 'SENIOR' | 'EXPERT' | 'UNSPECIFIED';

export interface JobListItem {
  source_name?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  id: string;
  title: string;
  company: string;
  level: JobLevel;
  status: JobStatus;
  created_at: string;
}

export interface JobCreateRequest {
  title: string;
  company: string;
  raw_description: string;
  level?: JobLevel;
}

export interface JobUpdateRequest {
  title?: string;
  company?: string;
  raw_description?: string;
  level?: JobLevel;
  status?: JobStatus;
}

export interface JobResponse {
  source_name?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  id: string;
  user_id: string;
  title: string;
  company: string;
  level: JobLevel;
  raw_description?: string;
  structured_data?: Record<string, unknown>;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  requirements: JobRequirement[];
}

// ── Match ──
export type MatchStatus = 'PENDING' | 'COMPLETED' | 'FAILED';

export interface MatchAnalyzeRequest {
  resume_ids: string[];
  job_id: string;
}

export interface MatchAnalyzeBatchResponse {
  results: MatchReportResponse[];
  total: number;
  succeeded: number;
  failed: number;
}

export interface MatchReportListItem {
  id: string;
  resume_id: string;
  job_id: string;
  overall_score?: number;
  status: MatchStatus;
  created_at: string;
}

export interface MatchReportResponse {
  id: string;
  resume_id: string;
  job_id: string;
  overall_score?: number;
  result_data?: MatchResultData;
  status: MatchStatus;
  created_at: string;
}

export interface MatchResultData {
  resume_analysis?: ResumeAnalysisResult;
  job_analysis?: JobAnalysisResult;
  match_result?: MatchAnalysisResult;
  report?: ReportResult;
}

export interface ResumeAnalysisResult {
  summary: string;
  skills: { name: string; level: string; category: string }[];
  experience_years: number;
  education_level: string;
  strengths: string[];
  weaknesses: string[];
  key_achievements: string[];
}

export interface JobAnalysisResult {
  job_title: string;
  required_skills: { name: string; importance: number; is_mandatory: boolean }[];
  education_requirement: string;
  experience_requirement: string;
  mandatory_requirements: string[];
  nice_to_have: string[];
}

export interface MatchAnalysisResult {
  overall_score: number;
  skill_match_score: number;
  experience_match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  strengths_analysis: string;
  gap_analysis: string;
}

export interface ReportResult {
  executive_summary: string;
  interview_suggestions: string[];
  hiring_recommendation: HiringRecommendation;
  follow_up_questions: string[];
}

export type HiringRecommendation =
  | 'strong_hire'
  | 'hire'
  | 'consider'
  | 'weak'
  | 'not_recommended';

// ── Knowledge ──
export interface KnowledgeDocumentCreate {
  id?: string;
  content: string;
  metadata?: Record<string, string>;
}

export interface KnowledgeSearchRequest {
  query: string;
  top_k?: number;
  where?: Record<string, string>;
}

export interface KnowledgeDocumentResponse {
  id: string;
  content: string;
  metadata: Record<string, string>;
  distance: number;
}

export interface KnowledgeSearchResponse {
  query: string;
  results: KnowledgeDocumentResponse[];
  total: number;
}

export interface KnowledgeCountResponse {
  total_documents: number;
}

export interface KnowledgeSeedResponse {
  message: string;
  documents_added: number;
}
