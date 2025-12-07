/**
 * Jobs API client for careers page
 */

import apiClient from './client';

export interface Job {
  id: number;
  title: string;
  department: string;
  location: string;
  employment_type: string;
  description: string;
  requirements: string;
  salary_range?: string | null;
  is_active: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
  application_count: number;
}

export interface JobCreate {
  title: string;
  department: string;
  location: string;
  employment_type: string;
  description: string;
  requirements: string;
  salary_range?: string;
  is_active?: boolean;
}

export interface JobUpdate {
  title?: string;
  department?: string;
  location?: string;
  employment_type?: string;
  description?: string;
  requirements?: string;
  salary_range?: string;
  is_active?: boolean;
}

export interface JobApplication {
  id: number;
  job_id: number;
  applicant_name: string;
  applicant_email: string;
  applicant_phone?: string | null;
  resume_url?: string | null;
  cover_letter: string;
  status: 'pending' | 'reviewing' | 'rejected' | 'accepted';
  created_at: string;
  updated_at: string;
  job_title?: string;
  job_department?: string;
}

export interface JobApplicationCreate {
  applicant_name: string;
  applicant_email: string;
  applicant_phone?: string;
  cover_letter: string;
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
  page: number;
  page_size: number;
}

export interface JobApplicationListResponse {
  applications: JobApplication[];
  total: number;
  page: number;
  page_size: number;
}

export const jobsApi = {
  // Public endpoints
  getJobs: (page: number = 1, pageSize: number = 20) =>
    apiClient.get<JobListResponse>('/api/v1/jobs/', { params: { page, page_size: pageSize, active_only: true } }),

  getJob: (id: number) =>
    apiClient.get<Job>(`/api/v1/jobs/${id}`),

  applyToJob: (id: number, data: JobApplicationCreate) =>
    apiClient.post<JobApplication>(`/api/v1/jobs/${id}/apply`, data),

  // Admin endpoints
  getAllJobsAdmin: (page: number = 1, pageSize: number = 20) =>
    apiClient.get<JobListResponse>('/api/v1/jobs/admin', { params: { page, page_size: pageSize } }),

  createJob: (data: JobCreate) =>
    apiClient.post<Job>('/api/v1/jobs/', data),

  updateJob: (id: number, data: JobUpdate) =>
    apiClient.put<Job>(`/api/v1/jobs/${id}`, data),

  deleteJob: (id: number) =>
    apiClient.delete(`/api/v1/jobs/${id}`),

  // Application management endpoints
  getApplications: (page: number = 1, pageSize: number = 20, jobId?: number, status?: string) =>
    apiClient.get<JobApplicationListResponse>('/api/v1/jobs/applications', {
      params: { page, page_size: pageSize, job_id: jobId, status }
    }),

  updateApplicationStatus: (id: number, status: string) =>
    apiClient.put<JobApplication>(`/api/v1/jobs/applications/${id}/status`, { status }),
};
