export type AuthUser = {
  id: string;
  email: string;
  role: string;
  plan_code: string | null;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
};
