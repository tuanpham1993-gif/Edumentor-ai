import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Mọi request bắt đầu bằng /api hoặc /uploads → chuyển sang backend FastAPI
      '/api': 'http://localhost:8000',      
      '/uploads': 'http://localhost:8000',  
    },
  },
});
