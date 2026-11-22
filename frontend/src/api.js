const DEFAULT_API_URL = import.meta.env.PROD
  ? "https://deepverify-x-api.onrender.com"
  : "http://127.0.0.1:8000";

const configuredApiUrl = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");
const usesLocalApi = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(
  configuredApiUrl
);

export const API_URL =
  import.meta.env.PROD && usesLocalApi
    ? DEFAULT_API_URL
    : configuredApiUrl || DEFAULT_API_URL;
