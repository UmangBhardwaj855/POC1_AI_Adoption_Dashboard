# Vercel Deployment Guide

## Prerequisites
1.  **GitHub Account**: This project should be pushed to a GitHub repository.
2.  **Vercel Account**: You need to be able to log in to [Vercel](https://vercel.com).
3.  **Database**: You need a cloud-hosted MySQL or PostgreSQL database.
    *   **Option A**: use [PlanetScale](https://planetscale.com/) (MySQL compatible).
    *   **Option B**: use [Supabase](https://supabase.com/) (PostgreSQL).
    *   **Option C**: use [Neon.tech](https://neon.tech/) (PostgreSQL).
    *   *Note*: The current code defaults to MySQL (`pymysql`). If using Postgres, you need to update `server/requirements.txt` to include `psycopg2-binary` and update the `DATABASE_URL` format.

## Setup Instructions

### 1. Push to GitHub
If you haven't already:
```bash
git init
git add .
git commit -m "Prepare for Vercel deployment"
# Add your remote origin
# git remote add origin https://github.com/yourusername/ai-dashboard.git
git push -u origin main
```

### 2. Import to Vercel
1.  Go to the Vercel Dashboard.
2.  Click **"Add New..."** -> **"Project"**.
3.  Select your GitHub repository `ai-adoption-dashboard`.
4.  **Important Configuration**:
    *   **Framework Preset**: Select **Vite** (Vercel typically auto-detects this from `client/package.json` but explicit is good. However, since we have a custom `vercel.json` config using `@vercel/static-build`, Vercel might default to "Other" which is fine).
    *   **Root Directory**: Leave it as `./` (Root). Do **NOT** change it to `client` or `server`. Our `vercel.json` handles the structure.
    *   **Build & Development Settings**: Leave these as default (managed by `vercel.json` and `package.json` scripts).

5.  **Environment Variables**:
    Expand the "Environment Variables" section and add:
    
    *   `DATABASE_URL`: Your cloud database connection string.
        *   Example (MySQL): `mysql+pymysql://user:password@host:port/dbname`
    *   `RESET_DB`: Set to `false` (prevents wiping the DB on every server restart). Set to `true` temporarily if you need to reset the schema.

### 3. Deploy
Click **"Deploy"**.

Vercel will:
1.  Build the Frontend (Vite) using `client/package.json`.
2.  Build the Backend (FastAPI) using `api/index.py` and `requirements.txt`.
3.  Deploy them to the generated URL.

## Troubleshooting

### Database Issues
If the app fails to load data or shows errors:
- Check "Runtime Logs" in Vercel Dashboard.
- Ensure `DATABASE_URL` is correct and accessible from the internet (0.0.0.0 allowed in DB firewall).
- If using SQLite locally (default): **This will NOT persist** on Vercel. You MUST use a cloud database.

### Python Requirements
- Dependencies are installed from the root `requirements.txt`.
- If a package is missing, add it to `requirements.txt`.

### Frontend/API Config
- The frontend is configured to send API requests to `/api`.
- The `vercel.json` rewrites `/api/*` to the Python backend.
- If you see 404s on API calls, check the `rewrites` or logs.
