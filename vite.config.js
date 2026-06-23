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
    outDir: 'static/css', 
    emptyOutDir: false, 
    rollupOptions: {
      input: 'static/css/input.css', 
      output: {
        assetFileNames: 'output.[ext]',
      },
    },
  },
})
