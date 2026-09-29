# Deployment

## Recommended first public deployment

Use a static host for Studio and the documentation. The browser runs the real Python model with Pyodide, so the prototype has no hosted Python service bill or server wake-up delay. Cloudflare Pages or GitHub Pages fit this design. The initial runtime download still requires internet access.

Build command:

```bash
python -m pip install -r requirements-web.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
```

Publish directory: `frontend/studio/dist`. All paths are relative so project-subpath hosting works. The provided **Publish web preview** workflow uploads a GitHub Pages artifact and deploys it when manually run after Pages is configured to use GitHub Actions. It does not change repository settings.

## Community address

The community link accepts the actual HTTPS address of your chosen forum or chat community. After creating it, put that address in the `url` field of `frontend/studio/public/community.json` and rebuild the frontend. Both Studio and the documentation use this setting. No account or community is provisioned by building or deploying this repository. FreeFlarum is an option for a separate hosted forum; GitHub Discussions can serve project discussions, and Discord can provide live chat. Check each provider's current limits before signup.

Leave the value empty until the community exists. The Studio then opens the community guide, whose Join link remains hidden. This file is public navigation configuration and must never contain credentials.

## Hosting options checked 28 September 2026

| Service | Suitable use | Limitation |
|---|---|---|
| Cloudflare Pages | Public Studio + docs | Static assets; Python runs in browser |
| GitHub Pages | Open-source project site | Repository Pages settings must be enabled |
| Render free web service | Optional native FastAPI demo | Sleeps after inactivity; cold start; not production availability |
| Vercel Hobby | Personal non-commercial frontend | Hobby terms restrict commercial use |
| Hugging Face Static Spaces | Static Python-in-browser demo | Runtime downloaded by browser |
| Hugging Face Docker Spaces | Native backend alternative | Current docs require paid PRO/Team to create Docker Spaces |

For native hosting, the included Dockerfile listens on `$PORT` (default 8000). Set the service's port and use `/api/health` as its health check. Run as an unprivileged user. Review concurrency and resource limits before admitting public traffic.

Primary sources: [Cloudflare limits](https://developers.cloudflare.com/pages/platform/limits/), [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages), [Render free services](https://render.com/docs/free), [Vercel Hobby](https://vercel.com/docs/plans/hobby), [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-overview), [Pyodide](https://pyodide.org/en/stable/).

Costs and terms can change. No hosting account, domain purchase or signing subscription is required to run the local preview.
