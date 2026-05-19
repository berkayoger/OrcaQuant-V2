import { storage } from "@/shared/lib/storage";

export type AuthUser = { id: string; email: string; role?: string; plan_code?: string | null };

export const authStore = {
  setSession: (accessToken: string, refreshToken: string, user?: AuthUser) => {
    storage.setAccessToken(accessToken);
    storage.setRefreshToken(refreshToken);
    if (user) localStorage.setItem("auth_user", JSON.stringify(user));
  },
  getUser: (): AuthUser | null => {
    const raw = localStorage.getItem("auth_user");
    if (!raw) return null;
    try { return JSON.parse(raw) as AuthUser; } catch { return null; }
  },
  isAuthenticated: (): boolean => Boolean(storage.getAccessToken()),
  clear: () => {
    storage.clearAuth();
    localStorage.removeItem("auth_user");
  },
};
