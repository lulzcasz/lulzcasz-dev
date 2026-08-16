import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/static/dist/' : '/',
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
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/[name].[ext]';
          }
          if (assetInfo.name && /\.(woff|woff2|eot|ttf|otf)$/.test(assetInfo.name)) {
            return 'webfonts/[name].[ext]';
          }
          return 'assets/[name].[ext]';
        },
      },
    },
  },
}))
