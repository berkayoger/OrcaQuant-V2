import { Navigate } from "react-router-dom";
import { PropsWithChildren } from "react";
import { authStore } from "./authStore";

export const AdminRoute = ({ children }: PropsWithChildren) => {
  if (!authStore.isAuthenticated()) return <Navigate to="/auth/login" replace />;
  const user = authStore.getUser();
  if (user?.role !== "admin") return <Navigate to="/" replace />;
  return <>{children}</>;
};
