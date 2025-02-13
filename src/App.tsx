import Layout from "components/ui/layout";
import "./App.css";
import AppRoutes from "./AppRoute";
import { BrowserRouter as Router } from "react-router-dom";
import SocketProvider from "socket/SocketContext";

const App = () => {
  return (
    <Router>
      <Layout>
        <SocketProvider>
          <AppRoutes />
        </SocketProvider>
      </Layout>
    </Router>
  );
};

export default App;
