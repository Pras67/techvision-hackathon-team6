import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { askGemini } from './api/chat.js';

// Runs /api/chat inside `npm run dev`, so the AI advisor works locally without Vercel.
function localApi(env) {
  return {
    name: 'local-api',
    configureServer(server) {
      server.middlewares.use('/api/chat', (req, res) => {
        if (req.method !== 'POST') { res.statusCode = 405; res.end(); return; }
        let raw = '';
        req.on('data', (c) => { raw += c; });
        req.on('end', async () => {
          let body = {};
          try { body = JSON.parse(raw || '{}'); } catch { /* empty body */ }
          const out = await askGemini(body, env);
          res.statusCode = out.status;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(out.body));
        });
      });
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = { ...process.env, ...loadEnv(mode, process.cwd(), '') };
  return { plugins: [react(), localApi(env)] };
});
