import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";
import { socketBaseUrl } from "utils/api";

// Creating the SocketContext
const SocketContext = createContext(null);

// Custom hook to access the socket context
export const useSocket = () => useContext(SocketContext);

// Socket Provider to manage socket connection
const SocketProvider = ({ children }: { children: ReactNode }) => {
  const [socket, setSocket] = useState(null);
  const [deviceId, setDeviceId] = useState("webclient");
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const socketInstance = new WebSocket(`${socketBaseUrl}${deviceId}`);

    // Function to handle reconnection
    const handleReconnect = () => {
      if (socketInstance.readyState !== WebSocket.OPEN) {
        console.log("Attempting to reconnect...");
        socketInstance.close(); // Close any previous connections
        setTimeout(() => {
          setSocket(new WebSocket(`${socketBaseUrl}${deviceId}`) as any); // Reconnect
        }, 1000); // Retry after 1 second
      }
    };

    // Event listeners for WebSocket connection
    socketInstance.onopen = () => {
      setIsConnected(true);
      console.log("WebSocket connected.");
    };

    socketInstance.onclose = (e) => {
      setIsConnected(false);
      console.log(`WebSocket closed. Reason: ${e.reason}`);
      handleReconnect(); // Attempt reconnect if connection is closed
    };

    socketInstance.onerror = (err) => {
      setIsConnected(false);
      console.log("WebSocket error: ", err);
      handleReconnect(); // Attempt reconnect on error
    };

    setSocket(socketInstance as any);

    // Cleanup WebSocket connection on component unmount
    return () => {
      if (socketInstance) {
        socketInstance.close();
      }
    };
  }, [deviceId]);

  return (
    <SocketContext.Provider value={{ socket, setDeviceId, isConnected } as any}>
      {children}
    </SocketContext.Provider>
  );
};

export default SocketProvider;
