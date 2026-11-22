# Deployment

The frontend is deployed to Vercel and the FastAPI service to Render.

## Vercel

1. Import this GitHub repository into Vercel and set the project root to `frontend`.
2. Deploy once to obtain the frontend URL.
3. The production frontend defaults to `https://deepverify-x-api.onrender.com`, the Render service created by `render.yaml`. Set `VITE_API_URL` only if the backend uses a different URL; use the full Render service URL with no trailing slash.
4. Redeploy after changing frontend code or `VITE_API_URL`.

`frontend/vercel.json` supplies the Vite build/output settings and SPA fallback.

## Render

1. Create a Blueprint from this repository and use the root `render.yaml`.
2. When prompted for `FRONTEND_ORIGINS`, enter the Vercel origin (for example, `https://your-project.vercel.app`). Separate multiple allowed origins with commas.
3. The blueprint uses Render's free instance plan. Free instances have limited memory and do not include persistent disks, so PyTorch may run out of memory and the local authentication database, uploads, reports, and analysis history can be lost when the service restarts or sleeps.
4. After deployment, copy the service URL into Vercel's `VITE_API_URL` as described above.

The Render build installs CPU-only PyTorch and the backend dependencies. The service runs one Uvicorn worker to limit memory use.

## Image model note

The current `ImageDetector` initializes torchvision's default ResNet18 weights at startup. The `.pth` files in `models/` are ignored by Git and are not loaded by that detector. If the deployed service must use one of those trained checkpoints, model loading and hosting that checkpoint need to be configured separately.
