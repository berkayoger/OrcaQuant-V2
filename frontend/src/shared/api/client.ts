import { storage } from "../lib/storage";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000/api/v1";

export class ApiError extends Error {
  constructor(public status: number, public payload: unknown) {
    super(`API ${status}`);
  }
}

export async function apiClient<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = storage.getAccessToken();
  const headers: HeadersInit = { "Content-Type": "application/json", ...(init.headers || {}) };
  if (token) (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // TODO(v1-migration): add a single refresh-token retry path for 401 responses.
    throw new ApiError(res.status, data);
  }
  return data as T;
}
