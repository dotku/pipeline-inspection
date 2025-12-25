"use client";

import { useState, useEffect } from "react";
import { getApiUrl } from "@/lib/config";

// Preset demo videos
const DEMO_PRESETS = {
  bigbuckbunny: "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
  rtspDemo: "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov",
};

export default function CameraSourceConfig() {
  const [isOpen, setIsOpen] = useState(false);
  const [sourceType, setSourceType] = useState<"usb" | "rtsp" | "http">("usb");
  const [usbIndex, setUsbIndex] = useState("0");
  const [streamUrl, setStreamUrl] = useState("");
  const [currentSource, setCurrentSource] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchCurrentSource();
  }, []);

  const fetchCurrentSource = async () => {
    try {
      const response = await fetch(getApiUrl("/api/camera/source"));
      const data = await response.json();
      setCurrentSource(data);

      // Set form values based on current source
      if (data.type === "USB") {
        setSourceType("usb");
        setUsbIndex(String(data.source));
      } else if (data.type === "RTSP") {
        setSourceType("rtsp");
        setStreamUrl(data.source);
      } else if (data.type === "HTTP") {
        setSourceType("http");
        setStreamUrl(data.source);
      }
    } catch (error) {
      console.error("Failed to fetch camera source:", error);
    }
  };

  const handleSave = async () => {
    setIsLoading(true);

    try {
      const source = sourceType === "usb" ? usbIndex : streamUrl;

      const response = await fetch(getApiUrl("/api/camera/source"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ source }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSource(data);
        setIsOpen(false);
        alert(data.message);
      } else {
        const error = await response.json();
        alert(`Failed to set camera source: ${error.detail}`);
      }
    } catch (error) {
      console.error("Error setting camera source:", error);
      alert("Failed to set camera source");
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentSource) return null;

  return (
    <div>
      {/* Config Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm flex items-center gap-2 transition-colors"
        title="Camera Source Configuration"
      >
        <svg
          className="w-4 h-4"
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
        <span className="hidden sm:inline">Camera</span>
      </button>

      {/* Config Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-lg shadow-2xl max-w-md w-full border border-slate-700">
            {/* Header */}
            <div className="border-b border-slate-700 px-6 py-4">
              <h2 className="text-xl font-bold text-white">
                Camera Source Configuration
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                Select USB camera, RTSP stream, or HTTP video
              </p>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              {/* Current Status */}
              <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-400">Current Source</span>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      currentSource.type === "USB"
                        ? "bg-blue-500/20 text-blue-400"
                        : currentSource.type === "RTSP"
                        ? "bg-purple-500/20 text-purple-400"
                        : "bg-green-500/20 text-green-400"
                    }`}
                  >
                    {currentSource.type}
                  </span>
                </div>
                <p className="text-xs text-slate-500 font-mono truncate">
                  {currentSource.source}
                </p>
              </div>

              {/* Source Type Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Source Type
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setSourceType("usb")}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      sourceType === "usb"
                        ? "bg-blue-600 text-white"
                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    USB
                  </button>
                  <button
                    onClick={() => setSourceType("rtsp")}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      sourceType === "rtsp"
                        ? "bg-purple-600 text-white"
                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    RTSP
                  </button>
                  <button
                    onClick={() => setSourceType("http")}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      sourceType === "http"
                        ? "bg-green-600 text-white"
                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    HTTP
                  </button>
                </div>
              </div>

              {/* USB Camera Index */}
              {sourceType === "usb" && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Camera Index
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={usbIndex}
                    onChange={(e) => setUsbIndex(e.target.value)}
                    placeholder="0"
                    className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Usually 0 for built-in camera, 1+ for external USB cameras
                  </p>
                </div>
              )}

              {/* RTSP/HTTP URL */}
              {(sourceType === "rtsp" || sourceType === "http") && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-slate-300">
                      {sourceType === "rtsp" ? "RTSP URL" : "HTTP Video URL"}
                    </label>
                    {sourceType === "http" && (
                      <button
                        onClick={() => setStreamUrl(DEMO_PRESETS.bigbuckbunny)}
                        className="text-xs text-blue-400 hover:text-blue-300"
                      >
                        Use Demo Video
                      </button>
                    )}
                  </div>
                  <input
                    type="text"
                    value={streamUrl}
                    onChange={(e) => setStreamUrl(e.target.value)}
                    placeholder={
                      sourceType === "rtsp"
                        ? "rtsp://example.com/stream"
                        : "https://example.com/video.mp4"
                    }
                    className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500 font-mono"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    {sourceType === "rtsp"
                      ? "Example: rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
                      : "Click 'Use Demo Video' for a sample or paste your own HTTP video URL"}
                  </p>
                </div>
              )}

              {/* Info Box */}
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
                    <p className="font-medium mb-1">Camera Source Options:</p>
                    <ul className="list-disc list-inside space-y-1 text-blue-400/80">
                      <li>
                        <strong>USB:</strong> Local camera connected to this device
                      </li>
                      <li>
                        <strong>RTSP:</strong> Network camera or video stream
                      </li>
                      <li>
                        <strong>HTTP:</strong> Video files from web servers
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-slate-700 px-6 py-4 flex gap-3">
              <button
                onClick={handleSave}
                disabled={
                  isLoading ||
                  ((sourceType === "rtsp" || sourceType === "http") && !streamUrl)
                }
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                {isLoading ? "Switching..." : "Apply & Restart Camera"}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
