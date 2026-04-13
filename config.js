/**
 * FreshPlate / Hotel Grand - Frontend Configuration
 * Replace %%BACKEND_URL%% with your actual Railway backend URL during deployment.
 * For local development, it falls back to localhost:5000.
 */
const CONFIG = {
    BACKEND_URL: "https://hotel-management-system-production-d4e9.up.railway.app"
};

// Fallback to localhost for development
if (CONFIG.BACKEND_URL === "%%BACKEND_URL%%" || CONFIG.BACKEND_URL === "") {
    CONFIG.BACKEND_URL = "http://localhost:5000";
}
