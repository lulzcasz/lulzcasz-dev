import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  server: {
    watch: {
      usePolling: true,
      interval: 3000,
    },
  },
  build: {
    outDir: 'static/dist',
    emptyOutDir: true, 
    rollupOptions: {
      input: {
        'main': 'static/js/main.js',
        'admin-editor': 'static/js/admin-editor.js',
        'style': 'static/css/style.css',
        'admin-style': 'static/css/admin-editor.css',
      }, 
      output: {
        entryFileNames: 'js/[name].js',
        assetFileNames: 'css/[name].[ext]',
      },
    },
  },
})
