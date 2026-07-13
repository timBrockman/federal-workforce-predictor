# GitHub Pages Setup (Out-of-the-Box)

This project uses the `/docs` folder for documentation. GitHub Pages can turn it into a nice browsable site with almost zero extra work.

## Steps for You (User)

1. Go to your repo on GitHub:
   Settings → Pages

2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: `master`
   - Folder: `/docs`
   - Click Save

3. Wait 1-2 minutes. Your site will be live at:
   https://timBrockman.github.io/federal-workforce-predictor/

4. (Recommended) Update repo settings:
   - Description: "Reference implementation of an ethics-first federal workforce / talent / critical-role readiness predictor. Demonstrates consent-aware auth, limited GraphQL + MCP, STRIDE-AI/OWASP/ATLAS, and NIST/FedRAMP/IL guidance."
   - Website: paste the Pages URL above
   - Topics: add `federal ai-ethics fastapi graphql mcp nist fedramp workforce reference-implementation ethics synthetic-data principal-model guardrails`
   - Enable "Discussions"
   - (Optional but nice) Mark as "Template repository"

## What Grok Has Prepared

- `docs/_config.yml` — minimal Jekyll config (title, nav, theme)
- `docs/index.md` — nice homepage with links and disclaimer
- `docs/.nojekyll` — prevents Jekyll from trying to process everything
- README now links to the Pages site

The site will automatically pick up changes to any file in `/docs` when you push to master.

## Tips for Best Experience

- All your existing Markdown files in subfolders (concepts/, compliance/, etc.) will render nicely.
- Links between docs should be relative (e.g. `concepts/ethics-and-consent.md`).
- The default Minima theme + our `_config.yml` gives clean navigation without any custom CSS.

No Cloudflare or custom domain needed — pure GitHub.

Once you enable Pages, let me know and I can help test links or add more polish.