"use client";

import { useState, useEffect } from "react";
import {
  getCurrentConfig,
  setCustomServerUrl,
  clearCustomServerUrl,
} from "@/lib/config";

export default function ServerConfig() {
  const [isOpen, setIsOpen] = useState(false);
  const [apiUrl, setApiUrl] = useState("");
  const [wsUrl, setWsUrl] = useState("");
  const [currentConfig, setCurrentConfig] = useState<any>(null);

  useEffect(() => {
    const config = getCurrentConfig();
    setCurrentConfig(config);
    setApiUrl(config.apiUrl);
    setWsUrl(config.wsUrl);
  }, []);

  const handleSave = () => {
    setCustomServerUrl(apiUrl, wsUrl);
    setCurrentConfig(getCurrentConfig());
    setIsOpen(false);

    // Reload page to apply new config
    window.location.reload();
  };

  const handleReset = () => {
    clearCustomServerUrl();
    setCurrentConfig(getCurrentConfig());
    setApiUrl(getCurrentConfig().apiUrl);
    setWsUrl(getCurrentConfig().wsUrl);
    setIsOpen(false);

    // Reload page to apply default config
    window.location.reload();
  };

  const handleAutoWs = () => {
    const autoWs = apiUrl.replace("http://", "ws://").replace("https://", "wss://");
    setWsUrl(autoWs);
  };

  if (!currentConfig) return null;

  return (
    <div>
      {/* Config Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm flex items-center gap-2 transition-colors"
        title="Server Configuration"
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
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <span className="hidden sm:inline">Server</span>
      </button>

      {/* Config Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-lg shadow-2xl max-w-md w-full border border-slate-700">
            {/* Header */}
            <div className="border-b border-slate-700 px-6 py-4">
              <h2 className="text-xl font-bold text-white">
                Server Configuration
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                Configure backend server connection
              </p>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              {/* Current Status */}
              <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-400">Current Mode</span>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      currentConfig.isCustom
                        ? "bg-blue-500/20 text-blue-400"
                        : "bg-green-500/20 text-green-400"
                    }`}
                  >
                    {currentConfig.isCustom ? "Custom" : "Default"}
                  </span>
                </div>
                <p className="text-xs text-slate-500">
                  API: {currentConfig.apiUrl}
                </p>
              </div>

              {/* API URL */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  API URL
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  placeholder="http://localhost:8000"
                  className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Examples: http://localhost:8000, http://192.168.1.100:8000
                </p>
              </div>

              {/* WebSocket URL */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center justify-between">
                  <span>WebSocket URL</span>
                  <button
                    onClick={handleAutoWs}
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    Auto-generate
                  </button>
                </label>
                <input
                  type="text"
                  value={wsUrl}
                  onChange={(e) => setWsUrl(e.target.value)}
                  placeholder="ws://localhost:8000"
                  className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Automatically generated from API URL or set manually
                </p>
              </div>

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
                    <p className="font-medium mb-1">Connection Examples:</p>
                    <ul className="list-disc list-inside space-y-1 text-blue-400/80">
                      <li>
                        <strong>Local:</strong> http://localhost:8000
                      </li>
                      <li>
                        <strong>LAN:</strong> http://192.168.1.100:8000
                      </li>
                      <li>
                        <strong>Public:</strong> https://api.yourserver.com
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
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Save & Reload
              </button>
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Reset
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
