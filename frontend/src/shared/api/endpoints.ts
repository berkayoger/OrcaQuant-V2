export const endpoints = {
  auth: { login: "/auth/login", register: "/auth/register", refresh: "/auth/refresh", logout: "/auth/logout" },
  user: { usage: "/me/usage" },
  billing: { status: "/billing/status", initiate: "/billing/initiate" },
};
