import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8080,
    host: '0.0.0.0', // Allow access from outside the container
    proxy: {
      '/api': {
        target: process.env.NODE_ENV === 'production' ? 'http://web-server:3000' : 'http://localhost:3000',
        changeOrigin: true
      },
      '/uploads': {
        target: process.env.NODE_ENV === 'production' ? 'http://web-server:3000' : 'http://localhost:3000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
}) 