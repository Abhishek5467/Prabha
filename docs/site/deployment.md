# Publish the web preview

The current website is a static Studio and documentation site. Python runs in the visitor's browser through Pyodide. This preview does not require AWS or a public Python server.

## Update the existing GitHub Pages site

1. Build and check your edited folder using [quick start](quickstart.md).
2. Commit and push the changes.
3. Confirm **Actions → Validate prototype** passes for your new commit.
4. Open **Actions → Publish web preview → Run workflow**. Choose the updated branch.
5. Wait for build and deploy to succeed.
6. Open [Studio](https://abhishek5467.github.io/Prabha/) and [documentation](https://abhishek5467.github.io/Prabha/docs/). Check the footer version, run the reference batch and test both community links.

Start a new workflow after each push. Re-running an old workflow uses its original commit. Validation alone does not update Pages.

For a new repository, first choose **Settings → Pages → Build and deployment → Source: GitHub Actions**. This repository's `.github/workflows/pages.yml` builds the Python assets, docs and frontend, then deploys the complete output. See [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## What gets built

```bash
python -m pip install -r requirements-web.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
```

Deploy `frontend/studio/dist`. It includes the Studio, Python source bundle, designer, documentation, community settings, evidence and source download. The relative Vite base supports repository subpaths.

Preview with `python -m http.server 8080 --directory frontend/studio/dist`. Use HTTP(S), not a local HTML file.

## Forum and Discord

Both are separate hosted communities, linked through `frontend/studio/public/community.json`:

```json
{
  "url": "https://prabhacommunity5701.flarum.cloud/",
  "chat_url": "https://discord.gg/RUdRMHBFp"
}
```

Edit this file and the fallback links in `docs/site/community.md` when an address changes. Rebuild and deploy. No membership synchronization or embedded chat server is required. See [community](community.md).

## Domain later

The GitHub Pages address is sufficient for the preview. If you buy a domain later, use [GitHub's custom domain guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site). Recheck Studio, docs, assets and community links after the DNS change.

For a native Python server on your computer, see [quick start](quickstart.md). Moving that server to a public host is a separate deployment decision.
