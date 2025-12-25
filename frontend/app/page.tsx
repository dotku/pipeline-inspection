"use client";

import { useState, useEffect } from "react";
import VideoStream from "@/components/VideoStream";
import DetectionLog from "@/components/DetectionLog";
import SystemStatus from "@/components/SystemStatus";
import ReportGenerator from "@/components/ReportGenerator";
import ServerConfig from "@/components/ServerConfig";
import { Detection } from "@/types";
import { getApiUrl } from "@/lib/config";

export default function Home() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch system status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(getApiUrl("/api/system/status"));
        const data = await response.json();
        setSystemStatus(data);
      } catch (error) {
        console.error("Failed to fetch system status:", error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleNewDetection = (detection: Detection) => {
    setDetections((prev) => [...prev, detection]);
  };

  const handleClearDetections = async () => {
    try {
      await fetch(getApiUrl("/api/detections/clear"), {
        method: "DELETE",
      });
      setDetections([]);
    } catch (error) {
      console.error("Failed to clear detections:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  Pipeline Inspection System
                </h1>
                <p className="text-sm text-slate-400">
                  AI-Powered Defect Detection
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <ServerConfig />

              <div
                className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                  isConnected
                    ? "bg-green-500/20 text-green-400"
                    : "bg-red-500/20 text-red-400"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? "bg-green-400" : "bg-red-400"
                  } animate-pulse`}
                />
                <span className="text-sm font-medium">
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Video Stream (2/3 width on desktop) */}
          <div className="lg:col-span-2 space-y-6">
            <VideoStream
              onNewDetection={handleNewDetection}
              onConnectionChange={setIsConnected}
            />

            <ReportGenerator
              detections={detections}
              onClearDetections={handleClearDetections}
            />
          </div>

          {/* Right Column - Status & Logs (1/3 width on desktop) */}
          <div className="lg:col-span-1 space-y-6">
            <SystemStatus status={systemStatus} />

            <DetectionLog detections={detections} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900/80 backdrop-blur-sm border-t border-slate-700 mt-12">
        <div className="container mx-auto px-4 py-4">
          <p className="text-center text-sm text-slate-400">
            Pipeline Inspection System v1.0.0 | Powered by YOLO + TensorFlow
          </p>
        </div>
      </footer>
    </div>
  );
}
