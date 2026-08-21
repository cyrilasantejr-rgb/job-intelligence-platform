// Mirrors backend/app/schemas/job.py — keep these in sync manually for now.
// (A generated-client step can replace this once the API stabilizes.)

export interface Company {
  id: number;
  name: string;
}

export interface Job {
  id: number;
  title: string;
  category: string | null;
  employment_type: string | null;
  location: string | null;
  work_mode: string | null;
  salary_min: number | null;
  salary_max: number | null;
  description: string | null;
  application_url: string | null;
  date_posted: string | null;
  deadline: string | null;
  created_at: string;
  company: Company;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
}

export interface JobFilters {
  category?: string;
  employment_type?: string;
  work_mode?: string;
  location?: string;
  search?: string;
  page?: number;
}

export const CATEGORIES = [
  "Software Engineering",
  "Data Engineering",
  "Data Analytics",
  "Machine Learning / AI",
  "Cloud / Platform Engineering",
] as const;

export const EMPLOYMENT_TYPES = ["Internship", "New Grad"] as const;

export const WORK_MODES = ["Remote", "Hybrid", "On-site"] as const;

// --- Application tracking ---

export const APPLICATION_STATUSES = [
  "Saved",
  "Applied",
  "Online Assessment",
  "Recruiter Screen",
  "Technical Interview",
  "Final Interview",
  "Offer",
  "Rejected",
  "Withdrawn",
] as const;

export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number];

export interface ApplicationJobSummary {
  id: number;
  title: string;
  location: string | null;
  company_name: string;
}

export interface Application {
  id: number;
  job_id: number;
  resume_id: number | null;
  current_status: string;
  date_applied: string | null;
  recruiter_contact: string | null;
  notes: string | null;
  created_at: string;
  job: ApplicationJobSummary;
}

export interface EventType {
  id: number;
  code: string;
  display_name: string;
  maps_to_status: string | null;
}

export interface ApplicationEvent {
  id: number;
  application_id: number;
  event_type: EventType;
  event_date: string;
  recorded_at: string;
  source: string | null;
  sender: string | null;
  subject: string | null;
  notes: string | null;
  is_automated: boolean | null;
  requires_response: boolean;
  responded: boolean;
  response_date: string | null;
  next_action: string | null;
  deadline: string | null;
  created_by: string;
}

