import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import httpProxy from 'http-proxy';

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        configure: (proxy: httpProxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log('[proxyReq] URL:', req.url, 'Headers:', req.headers);
          });
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log('[proxyRes] Status:', proxyRes.statusCode, 'URL:', req.url);
          });
          proxy.on('error', (err, req) => {
            console.error('[proxyError] URL:', req.url, 'Error:', err);
          });
        },
      }
    },
    host: '0.0.0.0'
  }
})

