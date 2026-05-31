import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API runs on :8000 (FastAPI). We proxy /api -> backend in dev so the
// frontend can use same-origin relative URLs and sidestep CORS entirely.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
