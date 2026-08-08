// Arrow Escape - Central API Configuration
export const API_BASE_URL = (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
    ? "http://127.0.0.1:8000"
    : "https://arrowescape.onrender.com";
export const API_V1_URL = `${API_BASE_URL}/api/v1`;
