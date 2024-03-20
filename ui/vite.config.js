import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  return {
    plugins: [react()],
    base: '',
    define: mode === 'development' ? {
      "__AUTH0_DOMAIN__": JSON.stringify(process.env.AUTH0_DOMAIN),
      "__AUTH0_CLIENT_ID__": JSON.stringify(process.env.AUTH0_CLIENT_ID),
      "__AUTH0_AUDIENCE__": JSON.stringify(process.env.AUTH0_AUDIENCE),
      "__REACT_APP_STRIPE_CLIENT_SECRET__": JSON.stringify(process.env.REACT_APP_STRIPE_CLIENT_SECRET),
      "__REACT_APP_STRIPE_PUBLIC_KEY__": JSON.stringify(process.env.REACT_APP_STRIPE_PUBLIC_KEY),
    } : {},
    build: {
      outDir: '../static',
      emptyOutDir: true,
    },
    server: {
      proxy: {
        '/api': 'http://127.0.0.1:8000'
      },
    },
  }
});
