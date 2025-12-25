"use client";

import { SystemStatus as SystemStatusType } from "@/types";

interface SystemStatusProps {
  status: SystemStatusType | null;
}

export default function SystemStatus({ status }: SystemStatusProps) {
  if (!status) {
    return (
      <div className="bg-slate-800 rounded-lg shadow-2xl overflow-hidden border border-slate-700 p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  const StatusRow = ({
    label,
    value,
    status: statusType,
  }: {
    label: string;
    value: string | number;
    status?: "success" | "error" | "warning";
  }) => {
    const statusColors = {
      success: "text-green-400",
      error: "text-red-400",
      warning: "text-yellow-400",
    };

    const statusColor = statusType ? statusColors[statusType] : "text-slate-300";

    return (
      <div className="flex items-center justify-between py-2">
        <span className="text-sm text-slate-400">{label}</span>
        <span className={`text-sm font-medium ${statusColor}`}>{value}</span>
      </div>
    );
  };

  return (
    <div className="bg-slate-800 rounded-lg shadow-2xl overflow-hidden border border-slate-700">
      {/* Header */}
      <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white">System Status</h2>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Camera Status */}
        <div className="bg-slate-900/30 rounded-lg p-3 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-3">
            <svg
              className="w-5 h-5 text-blue-400"
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
            <h3 className="font-semibold text-white">Camera</h3>
          </div>
          <div className="space-y-1">
            <StatusRow
              label="Status"
              value={status.camera.is_opened ? "Active" : "Inactive"}
              status={status.camera.is_opened ? "success" : "error"}
            />
            <StatusRow label="Device" value={`Camera ${status.camera.index}`} />
            <StatusRow label="Resolution" value={status.camera.resolution} />
            <StatusRow label="FPS" value={status.camera.fps} />
          </div>
        </div>

        {/* Detector Status */}
        <div className="bg-slate-900/30 rounded-lg p-3 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-3">
            <svg
              className="w-5 h-5 text-purple-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <h3 className="font-semibold text-white">AI Detector</h3>
          </div>
          <div className="space-y-1">
            <StatusRow
              label="Status"
              value={status.detector.is_loaded ? "Loaded" : "Not Loaded"}
              status={status.detector.is_loaded ? "success" : "error"}
            />
            <StatusRow
              label="Confidence"
              value={`${(status.detector.confidence_threshold * 100).toFixed(0)}%`}
            />
            <StatusRow
              label="Model"
              value={status.detector.model_path.split("/").pop() || "Unknown"}
            />
          </div>
        </div>

        {/* Detection Stats */}
        <div className="bg-slate-900/30 rounded-lg p-3 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-3">
            <svg
              className="w-5 h-5 text-green-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <h3 className="font-semibold text-white">Statistics</h3>
          </div>
          <div className="space-y-1">
            <StatusRow
              label="Total Detections"
              value={status.detections.total}
            />
            {status.detections.summary.average_confidence > 0 && (
              <StatusRow
                label="Avg Confidence"
                value={`${(status.detections.summary.average_confidence * 100).toFixed(1)}%`}
              />
            )}
          </div>

          {/* Detection by class */}
          {Object.keys(status.detections.summary.by_class).length > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-700">
              <p className="text-xs text-slate-400 mb-2">Detections by Type</p>
              <div className="space-y-1">
                {Object.entries(status.detections.summary.by_class).map(
                  ([className, count]) => (
                    <div
                      key={className}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-slate-400 capitalize">
                        {className.replace("_", " ")}
                      </span>
                      <span className="text-blue-400 font-medium">{count}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
