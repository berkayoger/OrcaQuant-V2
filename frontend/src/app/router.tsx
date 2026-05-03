import { createBrowserRouter } from "react-router-dom";
import HomePage from "../pages/public/HomePage";
import NotFoundPage from "../pages/public/NotFoundPage";
import LoginPage from "../pages/auth/LoginPage";
import DashboardPage from "../pages/app/DashboardPage";
import AdminDashboardPage from "../pages/admin/AdminDashboardPage";

export const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/app", element: <DashboardPage /> },
  { path: "/admin", element: <AdminDashboardPage /> },
  { path: "*", element: <NotFoundPage /> },
]);
