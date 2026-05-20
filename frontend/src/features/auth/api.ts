import { apiClient } from "@/shared/api/client";
import { endpoints } from "@/shared/api/endpoints";
import type { AuthResponse } from "./types";

export const login = (payload: { email: string; password: string }) =>
  apiClient<AuthResponse>(endpoints.auth.login, { method: "POST", body: JSON.stringify(payload) });

export const register = (payload: { email: string; password: string }) =>
  apiClient<AuthResponse>(endpoints.auth.register, { method: "POST", body: JSON.stringify(payload) });

export const refresh = (refresh_token: string) =>
  apiClient<AuthResponse>(endpoints.auth.refresh, {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });

export const logout = (refresh_token: string) =>
  apiClient<{ status: string }>(endpoints.auth.logout, { method: "POST", body: JSON.stringify({ refresh_token }) });
