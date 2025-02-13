import { Switch } from "components/ui";
import "./Main.scss";
import { useEffect, useState } from "react";
import Detections from "./Detections";
import { USER_MODES } from "enums";
import { useSocket } from "socket/SocketContext";

const { DETECTIONS, CAPTURING, RECORDINGS } = USER_MODES;

const modes = [
  {
    label: "Real-time Detections",
    value: DETECTIONS,
  },
  {
    label: "-",
    value: "",
  },
  {
    label: "Real-time Capturing",
    value: CAPTURING,
  },
  {
    label: "-",
    value: "",
  },
  {
    label: "Recordings",
    value: RECORDINGS,
  },
];

const Main = () => {
  const { socket, setDeviceId, isConnected }: any = useSocket() || {};

  console.log("inside main", socket, { isConnected });
  const [mode, setMode] = useState("DETECTIONS");
  const [deviceStatus, setDeviceStatus] = useState("Off");
  const [detections, setDetections] = useState<any[]>([]);

  const updateDetections = (newDetection: any) => {
    const { detections = [], texts = "" } = newDetection || {};
    setDetections((prevDetections: any[]) => [...prevDetections, newDetection]);
  };

  const handleSetMode = (mode: string) => {
    if (mode) {
      setMode(mode);
    }
  };

  useEffect(() => {
    if (!socket) return;

    // Listen for messages from the WebSocket server
    const handleMessage = (event: MessageEvent) => {
      const message = JSON.parse(event.data);

      if (message.event === "device_status") {
        setDeviceStatus(message.data.status);
      }

      if (message.event === "object_detection") {
        console.log("receievd");
        const { data } = message || {};
        // const {
        //   data: { detections, texts, time_taken },
        // } = data || {};
        // console.log({ texts, detections });
        updateDetections(data?.data);
      }
    };
    // check-device, object_detection, text_extraction

    socket?.addEventListener?.("message", handleMessage);

    return () => {
      socket?.removeEventListener?.("message", () => {});
    };
  }, [socket]);

  const renderBasedOnMode = () => {
    switch (mode) {
      case DETECTIONS:
        return <Detections detections={detections} />;
      case CAPTURING:
        return "";
      case RECORDINGS:
        return "";
      default:
        return "";
    }
  };

  return (
    <div className="main">
      <h4 className="flex-center gap-1">
        <span>Client Connection: {isConnected ? "On" : "Off"} -</span>
        <span>Device Status: Off -</span>
        <span className="flex-center">
          Recording Mode: <Switch />
        </span>
        <span className="flex-center">- Capture Mode: Detection</span>
      </h4>
      <div className="main__status_actions">
        {modes.map(({ label, value }) => (
          <p
            className={`${value === mode ? "active" : ""}`}
            onClick={() => handleSetMode(value)}
          >
            {label}
          </p>
        ))}
      </div>
      <br />
      {renderBasedOnMode()}
    </div>
  );
};

export default Main;
