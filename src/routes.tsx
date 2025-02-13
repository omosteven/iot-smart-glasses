import Main from "components/Main";
import Login from "./pages/Auth/Login/Login";
import Register from "./pages/Auth/Register/Register";

export const routes = [
  {
    route: "*",
    component: <Main />,
    subRoutes: [],
    title: "Dashboard",
    icon: "",
  },
  {
    route: "/register",
    component: <Register />,
    subRoutes: [],
    title: "Register",
    icon: "none",
  },
  {
    route: "/login",
    component: <Login />,
    subRoutes: [],
    title: "Login",
    icon: "",
  },
];
