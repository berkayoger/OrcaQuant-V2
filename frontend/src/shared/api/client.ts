import { storage } from "../lib/storage";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000/api/v1";

type ApiClientInit = RequestInit & { _retry401?: boolean };

export class ApiError extends Error {
  constructor(public status: number, public payload: unknown) {
    super(`API ${status}`);
  }
}

async function performRequest(path: string, init: ApiClientInit = {}): Promise<Response> {
  const token = storage.getAccessToken();
  const headers: HeadersInit = { "Content-Type": "application/json", ...(init.headers || {}) };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  return fetch(`${BASE_URL}${path}`, { ...init, headers });
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = storage.getRefreshToken();
  if (!refreshToken) {
    storage.clearAuth();
    return false;
  }

  const response = await fetch(`${BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Skip-Auth-Refresh": "true" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || !data?.access_token || !data?.refresh_token) {
    storage.clearAuth();
    return false;
  }

  storage.setAccessToken(data.access_token as string);
  storage.setRefreshToken(data.refresh_token as string);
  return true;
}

export async function apiClient<T>(path: string, init: ApiClientInit = {}): Promise<T> {
  const res = await performRequest(path, init);
  const data = await res.json().catch(() => ({}));

  const skipRefresh = typeof init.headers === "object" && init.headers !== null
    ? (init.headers as Record<string, string>)["X-Skip-Auth-Refresh"] === "true"
    : false;

  if (!res.ok) {
    const shouldTryRefresh = res.status === 401 && !init._retry401 && !skipRefresh;
    if (shouldTryRefresh) {
      const didRefresh = await refreshAccessToken();
      if (didRefresh) {
        const retryResponse = await performRequest(path, { ...init, _retry401: true });
        const retryData = await retryResponse.json().catch(() => ({}));
        if (!retryResponse.ok) {
          throw new ApiError(retryResponse.status, retryData);
        }
        return retryData as T;
      }
    }

    throw new ApiError(res.status, data);
  }

  return data as T;
}
