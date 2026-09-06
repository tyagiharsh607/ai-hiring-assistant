const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export type ScreeningCallRequest = {
  candidate_name: string;
  phone: string;
  job_description: string;
  role_title?: string;
};

export type CallTriggerResponse = {
  call_id: number;
  hunar_call_id: string | null;
  status: string;
};

export function triggerScreeningCall(body: ScreeningCallRequest) {
  return request<CallTriggerResponse>("/api/screening/calls", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type PdlCandidate = {
  name: string;
  title: string | null;
  company: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
};

export type SearchResponse = {
  job_description_id: number;
  candidates: PdlCandidate[];
};

export function searchCandidates(body: {
  job_description: string;
  role_title: string;
  location?: string;
  limit?: number;
}) {
  return request<SearchResponse>("/api/reachout/search", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function triggerReachoutCall(body: {
  job_description_id: number;
  name: string;
  phone: string;
  email?: string | null;
  title?: string | null;
  company?: string | null;
}) {
  return request<CallTriggerResponse>("/api/reachout/calls", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type DashboardCall = {
  call_id: number;
  flow: string;
  status: string;
  engagement_status: string | null;
  answered_by: string | null;
  candidate_name: string | null;
  candidate_phone: string | null;
  candidate_title: string | null;
  summary: string | null;
  transcript: string | null;
  recording_url: string | null;
  result: Record<string, unknown> | null;
  created_at: string;
};

export function listCalls() {
  return request<DashboardCall[]>("/api/dashboard/calls");
}

export function syncCalls() {
  return request<{ synced: number }>("/api/dashboard/sync", { method: "POST" });
}
