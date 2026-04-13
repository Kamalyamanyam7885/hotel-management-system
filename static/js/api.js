/**
 * FreshPlate / Hotel Grand - API Helper
 * Uses CONFIG.BACKEND_URL from config.js (loaded before this script).
 * All API calls should use these helper functions.
 */

const API = {
    /**
     * Get the base URL for backend API calls.
     * Falls back to localhost:5000 if CONFIG is not defined.
     */
    getBaseUrl: function () {
        if (typeof CONFIG !== "undefined" && CONFIG.BACKEND_URL) {
            return CONFIG.BACKEND_URL;
        }
        return "http://localhost:5000";
    },

    /**
     * Make a GET request to the backend API.
     * @param {string} endpoint - API endpoint (e.g., "/api/health")
     * @returns {Promise<Response>}
     */
    get: function (endpoint) {
        return fetch(this.getBaseUrl() + endpoint, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include"
        });
    },

    /**
     * Make a POST request to the backend API.
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @returns {Promise<Response>}
     */
    post: function (endpoint, data) {
        return fetch(this.getBaseUrl() + endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(data)
        });
    },

    /**
     * Check if the backend is healthy.
     * @returns {Promise<Object>}
     */
    healthCheck: async function () {
        try {
            const res = await this.get("/api/health");
            return await res.json();
        } catch (err) {
            console.error("Backend health check failed:", err);
            return { status: "error", message: err.message };
        }
    }
};
