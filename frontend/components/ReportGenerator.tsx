"use client";

import { useState } from "react";
import { Detection, InspectionMetadata } from "@/types";

interface ReportGeneratorProps {
  detections: Detection[];
  onClearDetections: () => void;
}

export default function ReportGenerator({
  detections,
  onClearDetections,
}: ReportGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [showMetadataForm, setShowMetadataForm] = useState(false);
  const [metadata, setMetadata] = useState<InspectionMetadata>({
    location: "",
    inspector: "",
    notes: "",
  });

  const handleGenerateReport = async (format: "pdf" | "json" | "both") => {
    if (detections.length === 0) {
      alert("No detections to generate report");
      return;
    }

    setIsGenerating(true);

    try {
      const response = await fetch("http://localhost:8000/api/report/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          metadata,
          format,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Download the files
        if (data.files.pdf) {
          const reportId = data.files.pdf.split("_").pop()?.split(".")[0];
          window.open(
            `http://localhost:8000/api/report/download/${reportId}?format=pdf`,
            "_blank"
          );
        }

        if (data.files.json) {
          const reportId = data.files.json.split("_").pop()?.split(".")[0];
          window.open(
            `http://localhost:8000/api/report/download/${reportId}?format=json`,
            "_blank"
          );
        }

        alert("Report generated successfully!");
        setShowMetadataForm(false);
      } else {
        alert(`Failed to generate report: ${data.detail}`);
      }
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Failed to generate report");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg shadow-2xl overflow-hidden border border-slate-700">
      {/* Header */}
      <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white">Report Generation</h2>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-900/30 rounded-lg p-3 border border-slate-700/50">
            <p className="text-xs text-slate-400 mb-1">Total Detections</p>
            <p className="text-2xl font-bold text-white">{detections.length}</p>
          </div>
          <div className="bg-slate-900/30 rounded-lg p-3 border border-slate-700/50">
            <p className="text-xs text-slate-400 mb-1">Unique Types</p>
            <p className="text-2xl font-bold text-white">
              {new Set(detections.map((d) => d.class_name)).size}
            </p>
          </div>
        </div>

        {/* Metadata Form */}
        {showMetadataForm && (
          <div className="bg-slate-900/30 rounded-lg p-4 border border-slate-700/50 space-y-3">
            <h3 className="text-sm font-semibold text-white mb-3">
              Inspection Details
            </h3>

            <div>
              <label className="block text-xs text-slate-400 mb-1">
                Location
              </label>
              <input
                type="text"
                value={metadata.location}
                onChange={(e) =>
                  setMetadata({ ...metadata, location: e.target.value })
                }
                placeholder="e.g., Building A - Basement"
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">
                Inspector Name
              </label>
              <input
                type="text"
                value={metadata.inspector}
                onChange={(e) =>
                  setMetadata({ ...metadata, inspector: e.target.value })
                }
                placeholder="e.g., John Doe"
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">
                Notes
              </label>
              <textarea
                value={metadata.notes}
                onChange={(e) =>
                  setMetadata({ ...metadata, notes: e.target.value })
                }
                placeholder="Additional notes..."
                rows={3}
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 resize-none"
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2">
          {!showMetadataForm ? (
            <button
              onClick={() => setShowMetadataForm(true)}
              disabled={detections.length === 0}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <svg
                className="w-5 h-5"
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
              Generate Report
            </button>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => handleGenerateReport("pdf")}
                disabled={isGenerating}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
              >
                {isGenerating ? "Generating..." : "PDF Only"}
              </button>
              <button
                onClick={() => handleGenerateReport("both")}
                disabled={isGenerating}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
              >
                {isGenerating ? "Generating..." : "PDF + JSON"}
              </button>
            </div>
          )}

          {showMetadataForm && (
            <button
              onClick={() => setShowMetadataForm(false)}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
            >
              Cancel
            </button>
          )}

          <button
            onClick={onClearDetections}
            disabled={detections.length === 0}
            className="w-full bg-red-600/20 hover:bg-red-600/30 disabled:bg-slate-700/50 text-red-400 disabled:text-slate-500 font-medium py-2 px-4 rounded-lg transition-colors text-sm border border-red-600/50 disabled:border-slate-700"
          >
            Clear All Detections
          </button>
        </div>

        {/* Info */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="flex gap-2">
            <svg
              className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="text-xs text-blue-300">
              <p className="font-medium mb-1">Report includes:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-400/80">
                <li>Detection summary and statistics</li>
                <li>Detailed findings with timestamps</li>
                <li>Confidence scores and locations</li>
                <li>Severity classification</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
