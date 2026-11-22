const DEFAULT_API_URL = import.meta.env.PROD
  ? "https://deepverify-x-api.onrender.com"
  : "http://127.0.0.1:8000";

export const API_URL = (
  import.meta.env.VITE_API_URL || DEFAULT_API_URL
).replace(/\/+$/, "");
