# Stable public link

**Share this URL (it never changes):**

https://finelogicscore-maker.github.io/iskon_ai/

Visitors are sent to the current Cloudflare tunnel where your app runs.

## One-time GitHub setup

1. Open https://github.com/finelogicscore-maker/iskon_ai/settings/pages
2. **Build and deployment** → Source: **Deploy from a branch**
3. Branch: **main**, folder: **/docs**
4. Save — wait 1–2 minutes for the site to go live.

## When you restart the tunnel

```bash
# Terminal 1 — API
uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2 — tunnel + auto-update redirect
./scripts/start-public.sh
```

`start-public.sh` updates `docs/tunnel-url.json` and pushes to GitHub so the stable link follows the new `trycloudflare.com` address.

To update the redirect without pushing:

```bash
AUTO_PUSH_REDIRECT=0 ./scripts/set-public-redirect.sh https://YOUR-new-url.trycloudflare.com
```

## Custom domain (optional)

In GitHub Pages settings, add a custom domain (e.g. `iskcon-ai.yourdomain.com`) — still the same redirect behavior.