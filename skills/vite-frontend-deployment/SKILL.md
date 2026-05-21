---
name: vite-frontend-deployment
description: Deploy/restart Vite-based frontend projects (React, Vue, etc.) for preview/sharing. Production build + preview, not dev mode.
---

# Vite Frontend Deployment

Deploy or redeploy a Vite-based frontend project (React, TypeScript, Vue, etc.) for LAN access.

## Triggers

- User says "启动" / "部署" / "更新了" for a Vite project
- User wants to serve a frontend project on the local network

## Prerequisites

Check before starting:
- `node_modules/` exists, otherwise `npm install` first
- Read `package.json` for the dev port (usually in the `dev` script, e.g. `--port=3000`)

## Workflow

### Initial Deployment
1. `npm install` (if node_modules missing)
2. `npm run build` — production build
3. Start preview server: `npx vite preview --port <PORT> --host 0.0.0.0` in background with notify_on_complete
4. Verify: `curl -s -o /dev/null -w '%{http_code}' http://localhost:<PORT>` → expect 200

### Redeploy (code updated)
1. Kill existing preview process
2. `git pull`
3. `npm run build`
4. `npx vite preview --port <PORT> --host 0.0.0.0` in background
5. Verify with curl localhost

## Pitfalls

- **Vite preview port**: `vite preview` defaults to port **4173**, NOT the port from `vite.config.ts` or the `dev` script. ALWAYS pass `--port <PORT>` explicitly to match the expected port.
- **Dev vs Preview**: User expects production build + preview, NOT `npm run dev`. Dev mode is slower for sharing/access.
- **Background**: Always use background mode for the preview server (it never exits).
- **Vite + Express hybrid**: If the project has `server.ts` with Express + Vite middleware, do NOT use `npm run dev` — the Vite middleware mode fails to serve the SPA (404 on `/`). See `references/vite-express-hybrid.md` for the full workflow.

## Access URL

Use user's local network IP from memory. Format: `http://<IP>:<PORT>`