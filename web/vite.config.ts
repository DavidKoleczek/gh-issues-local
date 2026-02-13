import path from "path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 10101,
    proxy: {
      "/api": "http://localhost:10100",
      "/repos": "http://localhost:10100",
      "/search": "http://localhost:10100",
      "/issues": "http://localhost:10100",
      "/orgs": "http://localhost:10100",
      "/user": "http://localhost:10100",
    },
  },
})
