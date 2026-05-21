# Vite + Express Hybrid Projects

Some projects bundle an Express backend with Vite frontend in a single repo.
These use `npm run dev` (tsx server.ts) for dev and `npm run build` + `npm run start` for production.

## Recognition

Look for:
- `server.ts` or `server.js` with Express + `createViteServer` (dev) / `express.static(dist)` (prod)
- `package.json` scripts: `"dev": "tsx server.ts"`, `"build": "vite build && esbuild server.ts ..."`, `"start": "node dist/server.cjs"`
- `better-sqlite3`, `bcryptjs`, `jsonwebtoken` in dependencies → full-stack app

## Why dev mode fails

`npm run dev` uses tsx + Vite middleware (`createViteServer({ middlewareMode: true })`).
The Vite middleware often fails to serve the SPA index.html fallback in this configuration,
returning 404 `Not Found` for `/` and all frontend routes. The Express API routes still work.

## Correct deployment flow

1. `npm install` (if node_modules missing)
2. **Check server.ts for hardcoded PORT** — patch if needed (e.g. `const PORT = 3001`)
3. `npm run build` — builds Vite frontend + bundles server.ts → `dist/server.cjs`
4. Start: `NODE_ENV=production npm run start` (or `NODE_ENV=production node dist/server.cjs`)
   - Use background=true, notify_on_complete=true
   - The server never exits, so don't wait for completion
5. Verify: `curl -s http://localhost:<PORT>/` → expect HTML (not 404)

## Common pitfalls

- PORT is hardcoded in server.ts, not read from env — must patch the file
- `npm run build` must succeed before `npm run start`
- NODE_ENV=production is required, otherwise it tries Vite middleware mode and fails
- The process runs forever (Express server), so background mode + health check is the way
