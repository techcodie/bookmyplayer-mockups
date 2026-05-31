// Typed API client for the OfferFunnel backend.
// In dev, Vite proxies /api → :8000. In production, set VITE_API_URL to the
// deployed backend root (e.g. https://offerfunnel.up.railway.app).
const BASE = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "offerfunnel_token";

export const token = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export type Stage =
  | "wishlist"
  | "applied"
  | "oa"
  | "interview"
  | "offer"
  | "rejected"
  | "ghosted";

export interface Application {
  id: number;
  company: string;
  role: string;
  job_url: string | null;
  location: string | null;
  source: string | null;
  salary_min: number | null;
  salary_max: number | null;
  interest_level: number;
  current_stage: Stage;
  applied_at: string | null;
  deadline: string | null;
  last_event_at: string;
  created_at: string;
  tags: string[];
}

export interface ApplicationEvent {
  id: number;
  from_stage: Stage | null;
  to_stage: Stage;
  note: string | null;
  occurred_at: string;
}

export interface ApplicationDetail extends Application {
  events: ApplicationEvent[];
}

export interface FocusItem extends Application {
  priority_score: number;
}

export interface FunnelStep {
  stage: string;
  reached: number;
  conversion: number | null;
}

export interface Funnel {
  steps: FunnelStep[];
  biggest_dropoff: { from: string; to: string; conversion: number } | null;
}

export interface Summary {
  total: number;
  active: number;
  applied: number;
  responded: number;
  offers: number;
  response_rate: number | null;
  offer_rate: number | null;
  avg_time_to_response_days: number | null;
}

export interface VelocityStep {
  stage: string;
  avg_days: number;
  n: number;
}

export type ReminderType = "follow_up" | "deadline" | "interview";
export interface Reminder {
  id: number;
  application_id: number;
  type: ReminderType;
  due_at: string;
  message: string;
  is_done: boolean;
}

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string>),
  };
  const t = token.get();
  if (t) headers.Authorization = `Bearer ${t}`;

  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (res.status === 204) return undefined as T;
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return body as T;
}

export const api = {
  async login(email: string, password: string) {
    // OAuth2 password form expects urlencoded username/password.
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.detail || "Login failed");
    token.set(body.access_token);
    return body.access_token as string;
  },
  register: (email: string, password: string, name?: string) =>
    req("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    }),

  listApplications: (q = "") =>
    req<Application[]>(`/applications${q}`),
  getApplication: (id: number) =>
    req<ApplicationDetail>(`/applications/${id}`),
  createApplication: (data: Partial<Application> & { initial_stage?: Stage }) =>
    req<Application>("/applications", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  transition: (id: number, to_stage: Stage, note?: string) =>
    req<ApplicationEvent>(`/applications/${id}/transition`, {
      method: "POST",
      body: JSON.stringify({ to_stage, note }),
    }),
  addTag: (id: number, name: string) =>
    req<{ id: number; name: string }[]>(`/applications/${id}/tags`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  funnel: () => req<Funnel>("/analytics/funnel"),
  summary: () => req<Summary>("/analytics/summary"),
  velocity: () => req<VelocityStep[]>("/analytics/velocity"),

  focusToday: () => req<FocusItem[]>("/focus/today"),
  reminders: (openOnly = false) =>
    req<Reminder[]>(`/reminders${openOnly ? "?due=true" : ""}`),
  resolveReminder: (id: number) =>
    req<Reminder>(`/reminders/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ is_done: true }),
    }),
};
