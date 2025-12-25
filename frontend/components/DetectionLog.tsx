"use client";

import { Detection } from "@/types";
import { useEffect, useRef } from "react";

interface DetectionLogProps {
  detections: Detection[];
}

const DEFECT_COLORS: Record<string, string> = {
  foreign_object: "text-red-400",
  crack: "text-orange-400",
  rust: "text-yellow-400",
  corrosion: "text-amber-400",
  sediment: "text-brown-400",
  leak: "text-blue-400",
};

const DEFECT_ICONS: Record<string, string> = {
  foreign_object: "⚠️",
  crack: "🔴",
  rust: "🟠",
  corrosion: "🟡",
  sediment: "🟤",
  leak: "💧",
};

export default function DetectionLog({ detections }: DetectionLogProps) {
  const logRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new detection arrives
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [detections]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const formatClassName = (className: string) => {
    return className
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div className="bg-slate-800 rounded-lg shadow-2xl overflow-hidden border border-slate-700">
      {/* Header */}
      <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Detection Log</h2>
          <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm font-medium">
            {detections.length}
          </span>
        </div>
      </div>

      {/* Log Content */}
      <div
        ref={logRef}
        className="h-96 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-900"
      >
        {detections.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-slate-500">
              <svg
                className="w-12 h-12 mx-auto mb-3 opacity-50"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-sm">No detections yet</p>
              <p className="text-xs mt-1">Waiting for defects...</p>
            </div>
          </div>
        ) : (
          detections.slice().reverse().map((detection, index) => {
            const actualIndex = detections.length - 1 - index;
            const colorClass =
              DEFECT_COLORS[detection.class_name] || "text-gray-400";
            const icon = DEFECT_ICONS[detection.class_name] || "🔍";

            return (
              <div
                key={`${detection.timestamp}-${actualIndex}`}
                className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className={`font-semibold ${colorClass}`}>
                        {formatClassName(detection.class_name)}
                      </span>
                      <span className="text-xs text-slate-500">
                        {formatTime(detection.timestamp)}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span>
                        Confidence:{" "}
                        <span className="text-green-400 font-mono">
                          {(detection.confidence * 100).toFixed(1)}%
                        </span>
                      </span>
                      {detection.frame_position && (
                        <span>
                          Position:{" "}
                          <span className="text-blue-400 font-mono">
                            {detection.frame_position}m
                          </span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Stats */}
      {detections.length > 0 && (
        <div className="bg-slate-900/30 px-4 py-2 border-t border-slate-700">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total: {detections.length} detections</span>
            <span>
              Avg Confidence:{" "}
              {(
                (detections.reduce((sum, d) => sum + d.confidence, 0) /
                  detections.length) *
                100
              ).toFixed(1)}
              %
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
