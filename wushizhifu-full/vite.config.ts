import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    // Generate version based on build time (format: YYYYMMDDHHmmss)
    // This ensures each build has a unique version, forcing cache clear in Telegram WebView
    const buildVersion = new Date().toISOString().replace(/[-:T]/g, '').split('.')[0];
    return {
      // Explicitly set public directory
      publicDir: 'public',
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        // Add version for cache busting - uses build timestamp to ensure unique version per build
        'process.env.APP_VERSION': JSON.stringify(buildVersion)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      build: {
        // Ensure file names include hash for cache busting
        rollupOptions: {
          output: {
            entryFileNames: 'assets/[name]-[hash].js',
            chunkFileNames: 'assets/[name]-[hash].js',
            assetFileNames: 'assets/[name]-[hash].[ext]'
          }
        }
      }
    };
});
