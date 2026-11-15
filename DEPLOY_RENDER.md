# Deploy ISKCON AI on Render

## Prerequisites

- [Render](https://render.com) account
- Git repo on **GitHub**, **GitLab**, or **Bitbucket** with this project (no `.env` in the repo)
- `PINECONE_API_KEY` and `GOOGLE_API_KEY` from your local `.env`

## Recommended instance size

This app loads **sentence-transformers** on the server (~500MB+ RAM). Use at least **Starter (512MB)**; **Standard (2GB)** is safer for stable cold starts.

## Option A: Blueprint (`render.yaml`)

1. Push this folder to a new Git repository.
2. In Render: **New** → **Blueprint** → connect the repo.
3. When prompted, set **secret** env vars:
   - `PINECONE_API_KEY`
   - `GOOGLE_API_KEY`
4. Apply the blueprint and wait for the build (first build may take 10–15 minutes).

## Option B: Manual Web Service

1. **New** → **Web Service** → connect your repo.
2. Settings:
   - **Runtime:** Python 3
   - **Build command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/health`
3. **Environment** → add `PINECONE_API_KEY`, `GOOGLE_API_KEY`, and optionally `PYTHON_VERSION=3.11.9`.
4. Deploy.

## Pinecone index names

Chat routes use URL paths that must match your Pinecone index names:

- `chaitanya`
- `bhagwad-gita`
- `bhagwatam`
- `prabhupad`

## After deploy

Open the Render service URL. Test `/health`, then the home page and a chat on one book.