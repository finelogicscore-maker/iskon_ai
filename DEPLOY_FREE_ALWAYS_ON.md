# Free hosting with no cold starts (unlike Render)

## Why Render feels slow

1. **Free Render sleeps** after ~15 minutes with no traffic.
2. On wake, the server must **boot Python + PyTorch + sentence-transformers** (~1 GB RAM, often 1–3 minutes).

“Instant” means the app **stays running 24/7**. Most free PaaS (Render, Railway hobby, Cloud Run scale-to-zero) sleep or restart.

This project **must** keep the same embedding model (`all-MiniLM-L6-v2`) as your Pinecone indexes, so the API needs a small always-on server with **≥ 2 GB RAM** (1 GB is tight).

---

## Best free option: Oracle Cloud “Always Free” VM

- **Cost:** $0/month (Always Free ARM VM — up to 4 OCPUs, 24 GB RAM in eligible shapes)
- **Cold start:** None for users — Uvicorn + model load **once** at boot; then instant until you redeploy
- **Tradeoff:** One-time setup (SSH, firewall, systemd)

### Outline

1. Sign up: [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Create an **Ampere A1** compute instance (Ubuntu 22.04), open port **80/443** (or 8000 for testing).
3. SSH in, install dependencies:

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv git
git clone git@github.com:finelogicscore-maker/iskon_ai.git
cd iskon_ai
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export PINECONE_API_KEY=...
export GOOGLE_API_KEY=...
uvicorn main:app --host 0.0.0.0 --port 8000
```

4. Run under **systemd** so it restarts on reboot (ask in chat for a ready-made `iskcon-ai.service` unit file).
5. Optional: **Nginx** reverse proxy + **Let’s Encrypt** for HTTPS on your domain.

Your repo is already on GitHub: `finelogicscore-maker/iskon_ai`.

---

## Alternative: Home PC + Cloudflare Tunnel (free, instant)

If a Mac/PC can stay on:

1. Run `uvicorn main:app --host 127.0.0.1 --port 8000` locally.
2. Install [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) and create a tunnel to a free `*.trycloudflare.com` or your domain.
3. **No sleep**, no Render cold start — limited by your home uptime and bandwidth.

---

## What does *not* fit well (for this app)

| Platform | Issue |
|----------|--------|
| Render free | Sleeps + very slow wake (model load) |
| Vercel / Netlify serverless | No long-running PyTorch; huge cold starts |
| Hugging Face Spaces free | Sleeps after ~48h inactivity; Docker may need paid plan |
| 512 MB “always on” hosts | Often **OOM** with sentence-transformers + torch |

---

## If you stay on Render

Upgrade to a **paid** instance with **≥ 2 GB RAM** and disable auto-sleep (paid web services don’t spin down like free tier). Still slower on **deploy** than Oracle, but usable for demos.

---

## Recommended path

**Oracle Always Free VM (2+ GB)** for production-like free hosting, or **Cloudflare Tunnel at home** for the fastest path with zero cloud billing.

If you want, we can add a `deploy/iskcon-ai.service` systemd file and a one-shot setup script for Oracle in this repo.