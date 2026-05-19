import { Navigate } from "react-router-dom";
import { PropsWithChildren } from "react";
import { authStore } from "./authStore";

export const ProtectedRoute = ({ children }: PropsWithChildren) => {
  if (!authStore.isAuthenticated()) return <Navigate to="/auth/login" replace />;
  return <>{children}</>;
};
