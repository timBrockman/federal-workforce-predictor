# v0.1.0 - Initial Public Release (GitHub Pages Docs)

## Highlights

- **Out-of-the-box GitHub Pages documentation site** now available at https://timBrockman.github.io/federal-workforce-predictor/
  - Powered directly from the `/docs` folder using standard GitHub Pages + Jekyll.
  - Includes clean homepage, navigation, and all existing rich Markdown content (concepts, compliance, threat models, usage, etc.).
  - Makes the documentation much more approachable and browsable than raw repo tree view.

- Strong, prominent disclaimers added throughout (README, docs, compliance sections) emphasizing this is a **reference/educational template only** — not for production, not an ATO, verify current regulations.

- Enhanced GitHub experience:
  - New issue templates for compliance/federal questions and feature/pattern suggestions.
  - Improved CI workflow with better caching.
  - CODE_OF_CONDUCT removed (per request).

## What's Included

- Full reference implementation (FastAPI + Strawberry GraphQL limited schema, MCP stdio server, async SQLAlchemy + Alembic, Principal + consent model, EthicalPolicy with decision logging).
- Synthetic-data-only discipline.
- STRIDE-AI + OWASP LLM/Agentic + MITRE ATLAS threat modeling (7 examples).
- NIST AI RMF crosswalk and IL deployment guidance (skeletons with real mappings).
- Comprehensive tests + one-shot `scripts/verify.py`.
- Rich documentation under `/docs`.

## Getting Started

See the [README](https://github.com/timBrockman/federal-workforce-predictor) or the new [documentation site](https://timBrockman.github.io/federal-workforce-predictor/).

```bash
git clone https://github.com/timBrockman/federal-workforce-predictor.git
cd federal-workforce-predictor
uv sync --extra dev
uv run python scripts/verify.py
```

## Important

This is a **reference implementation and educational template**. It is not certified for any compliance framework. Always obtain your own ATO and perform due diligence.

## What's Next

- Feedback on the patterns (Principal model, ethics enforcement, limited interfaces, etc.).
- Contributions to expand compliance docs, threat models, or examples.
- Future: possible PyPI packaging for core utilities (not planned yet).

Thanks to everyone who helped shape the federal pivot and GitHub prep!
