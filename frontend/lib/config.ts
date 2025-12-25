/**
 * Frontend API Configuration
 * Supports multiple deployment scenarios
 */

export const config = {
  // API Base URL
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

  // WebSocket URL
  wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',

  // Mock mode (for demos without backend)
  mockMode: process.env.NEXT_PUBLIC_MOCK_MODE === 'true',

  // Enable runtime configuration (allows users to change server)
  // Default to true for better UX, can be disabled by setting to 'false'
  allowRuntimeConfig: process.env.NEXT_PUBLIC_ALLOW_RUNTIME_CONFIG !== 'false',
};

/**
 * Get API endpoint URL
 */
export function getApiUrl(path: string = ''): string {
  // Check if user has overridden via localStorage (runtime config)
  if (typeof window !== 'undefined' && config.allowRuntimeConfig) {
    const customApiUrl = localStorage.getItem('custom_api_url');
    if (customApiUrl) {
      return `${customApiUrl}${path}`;
    }
  }

  return `${config.apiUrl}${path}`;
}

/**
 * Get WebSocket URL
 */
export function getWebSocketUrl(path: string = ''): string {
  // Check if user has overridden via localStorage
  if (typeof window !== 'undefined' && config.allowRuntimeConfig) {
    const customWsUrl = localStorage.getItem('custom_ws_url');
    if (customWsUrl) {
      return `${customWsUrl}${path}`;
    }
  }

  return `${config.wsUrl}${path}`;
}

/**
 * Set custom server URL (runtime configuration)
 */
export function setCustomServerUrl(apiUrl: string, wsUrl?: string): void {
  if (typeof window === 'undefined') return;

  localStorage.setItem('custom_api_url', apiUrl);

  if (wsUrl) {
    localStorage.setItem('custom_ws_url', wsUrl);
  } else {
    // Auto-generate WebSocket URL from API URL
    const wsUrlAuto = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    localStorage.setItem('custom_ws_url', wsUrlAuto);
  }
}

/**
 * Clear custom server configuration
 */
export function clearCustomServerUrl(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem('custom_api_url');
  localStorage.removeItem('custom_ws_url');
}

/**
 * Get current server configuration
 */
export function getCurrentConfig() {
  return {
    apiUrl: getApiUrl(),
    wsUrl: getWebSocketUrl(),
    mockMode: config.mockMode,
    isCustom: typeof window !== 'undefined' &&
              !!localStorage.getItem('custom_api_url'),
  };
}
