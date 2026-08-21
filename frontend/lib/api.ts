import { Application, ApplicationEvent, EventType, JobFilters, JobListResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Fetches the job listing from the backend with optional filters.
 *
 * Runs server-side (this is called from a Server Component), so there's
 * no loading spinner needed for the initial page load — Next.js renders
 * the page only once the data is ready.
 */
export async function fetchJobs(filters: JobFilters): Promise<JobListResponse> {
  const params = new URLSearchParams();

  if (filters.category) params.set("category", filters.category);
  if (filters.employment_type) params.set("employment_type", filters.employment_type);
  if (filters.work_mode) params.set("work_mode", filters.work_mode);
  if (filters.location) params.set("location", filters.location);
  if (filters.search) params.set("search", filters.search);
  params.set("page", String(filters.page ?? 1));
  params.set("page_size", "12");

  const response = await fetch(`${API_BASE_URL}/jobs?${params.toString()}`, {
    // Always fetch fresh data — job listings change frequently and this
    // is a dashboard-style app, not a page that benefits from caching.
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch jobs: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// --- Application tracking ---

export async function fetchApplications(): Promise<Application[]> {
  const response = await fetch(`${API_BASE_URL}/applications`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch applications: ${response.status}`);
  }
  return response.json();
}

export async function fetchApplication(id: number): Promise<Application> {
  const response = await fetch(`${API_BASE_URL}/applications/${id}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch application: ${response.status}`);
  }
  return response.json();
}

export async function fetchApplicationEvents(id: number): Promise<ApplicationEvent[]> {
  const response = await fetch(`${API_BASE_URL}/applications/${id}/events`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch events: ${response.status}`);
  }
  return response.json();
}

export async function fetchEventTypes(): Promise<EventType[]> {
  const response = await fetch(`${API_BASE_URL}/event-types`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch event types: ${response.status}`);
  }
  return response.json();
}

export async function createApplication(jobId: number): Promise<Application> {
  const response = await fetch(`${API_BASE_URL}/applications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id: jobId }),
  });
  if (!response.ok) {
    throw new Error(`Failed to create application: ${response.status}`);
  }
  return response.json();
}

export async function updateApplicationStatus(id: number, newStatus: string): Promise<Application> {
  const response = await fetch(`${API_BASE_URL}/applications/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ new_status: newStatus }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update status: ${response.status}`);
  }
  return response.json();
}

export interface CreateEventInput {
  event_type_code: string;
  event_date?: string;
  source?: string;
  sender?: string;
  subject?: string;
  notes?: string;
  is_automated?: boolean;
  requires_response?: boolean;
  next_action?: string;
  deadline?: string;
}

export async function createApplicationEvent(
  applicationId: number,
  input: CreateEventInput
): Promise<ApplicationEvent> {
  const response = await fetch(`${API_BASE_URL}/applications/${applicationId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`Failed to log event: ${response.status}`);
  }
  return response.json();
}
