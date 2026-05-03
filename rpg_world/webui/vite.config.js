import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

const settings = JSON.parse(
  readFileSync(resolve(__dirname, 'settings.json'), 'utf-8'),
)

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  define: {
    __API_HOST__: JSON.stringify(settings.api_host ?? '127.0.0.1'),
    __API_PORT__: JSON.stringify(settings.api_port ?? 8000),
  },
  server: {
    port: settings.port ?? 5173,
    proxy: {
      '/api': {
        target: `http://${settings.api_host}:${settings.api_port}`,
        changeOrigin: true,
      },
    },
  },
})
