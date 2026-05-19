import { apiClient } from "@/shared/api/client";
import { endpoints } from "@/shared/api/endpoints";

export const login = (payload: { email: string; password: string }) => apiClient(endpoints.auth.login, { method: "POST", body: JSON.stringify(payload) });
export const register = (payload: { email: string; password: string }) => apiClient(endpoints.auth.register, { method: "POST", body: JSON.stringify(payload) });
