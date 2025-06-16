import { sentryVitePlugin } from '@sentry/vite-plugin'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: '/static/',
  plugins: [
    vue(),
    sentryVitePlugin({
      org: 'django-3x',
      project: 'javascript-vue',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend'),
    },
  },
  build: {
    manifest: 'manifest.json',
    outDir: path.resolve('./assets'),

    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'frontend/main.ts'),
      },
    },

    sourcemap: true,
  },
})
