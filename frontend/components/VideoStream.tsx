"use client";

import { useEffect, useRef, useState } from "react";
import { Detection } from "@/types";
import { getWebSocketUrl } from "@/lib/config";

interface VideoStreamProps {
  onNewDetection: (detection: Detection) => void;
  onConnectionChange: (isConnected: boolean) => void;
}

export default function VideoStream({
  onNewDetection,
  onConnectionChange,
}: VideoStreamProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [fps, setFps] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const lastFrameTime = useRef(Date.now());
  const frameCount = useRef(0);

  // Store callbacks in refs to avoid reconnection on callback changes
  const onNewDetectionRef = useRef(onNewDetection);
  const onConnectionChangeRef = useRef(onConnectionChange);

  // Update refs when callbacks change
  useEffect(() => {
    onNewDetectionRef.current = onNewDetection;
    onConnectionChangeRef.current = onConnectionChange;
  }, [onNewDetection, onConnectionChange]);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(getWebSocketUrl("/ws/video"));
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket connected");
        setIsStreaming(true);
        onConnectionChangeRef.current(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.error) {
            console.error("Stream error:", data.error);
            return;
          }

          // Draw frame on canvas
          if (data.frame && canvasRef.current) {
            const img = new Image();
            img.onload = () => {
              const canvas = canvasRef.current;
              if (!canvas) return;

              const ctx = canvas.getContext("2d");
              if (!ctx) return;

              // Set canvas size to match image
              canvas.width = img.width;
              canvas.height = img.height;

              // Draw image
              ctx.drawImage(img, 0, 0);

              // Update FPS
              frameCount.current++;
              const now = Date.now();
              const elapsed = now - lastFrameTime.current;

              if (elapsed >= 1000) {
                setFps(Math.round((frameCount.current * 1000) / elapsed));
                frameCount.current = 0;
                lastFrameTime.current = now;
              }
            };
            img.src = `data:image/jpeg;base64,${data.frame}`;
          }

          // Handle detections
          if (data.detections && data.detections.length > 0) {
            data.detections.forEach((detection: Detection) => {
              onNewDetectionRef.current(detection);
            });
          }
        } catch (error) {
          console.error("Error processing frame:", error);
        }
      };

      ws.onerror = (error) => {
        // Suppress empty error objects (normal during reconnection)
        if (Object.keys(error).length > 0) {
          console.error("WebSocket error:", error);
        }
        setIsStreaming(false);
        onConnectionChangeRef.current(false);
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setIsStreaming(false);
        onConnectionChangeRef.current(false);

        // Attempt reconnection after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []); // Empty deps - callbacks accessed via refs

  return (
    <div className="bg-slate-800 rounded-lg shadow-2xl overflow-hidden border border-slate-700">
      {/* Header */}
      <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          <h2 className="text-lg font-semibold text-white">Live Video Feed</h2>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">FPS:</span>
            <span className="text-green-400 font-mono font-bold">{fps}</span>
          </div>

          <div
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              isStreaming
                ? "bg-green-500/20 text-green-400"
                : "bg-red-500/20 text-red-400"
            }`}
          >
            {isStreaming ? "Streaming" : "Offline"}
          </div>
        </div>
      </div>

      {/* Video Canvas */}
      <div className="relative bg-black aspect-video flex items-center justify-center">
        <canvas
          ref={canvasRef}
          className="max-w-full max-h-full w-auto h-auto"
        />

        {!isStreaming && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80">
            <div className="text-center">
              <svg
                className="w-16 h-16 text-slate-600 mx-auto mb-4 animate-pulse"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              <p className="text-slate-400">Connecting to camera...</p>
            </div>
          </div>
        )}
      </div>

      {/* Help Text */}
      <div className="bg-slate-900/30 px-4 py-2 text-xs text-slate-400 border-t border-slate-700">
        <p>
          Real-time detection with YOLO. Defects are highlighted with bounding
          boxes and confidence scores.
        </p>
      </div>
    </div>
  );
}
