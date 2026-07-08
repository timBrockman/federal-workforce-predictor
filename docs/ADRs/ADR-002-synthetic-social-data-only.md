# ADR-002: Synthetic / Mocked Social Data Only

## Status

Accepted

## Context

The product vision involves "social media signals" to improve budget recommendations. Real social data brings severe legal, privacy, ethical, and ToS problems.

## Decision

All social signals in the reference implementation are **synthetic and versioned**.

- `SYNTHETIC_PROFILES` in `recommender.py`
- Clearly attributed in responses (`dataSources` includes `"synthetic_social"` only when consent allows)
- Never attempts to ingest or store real user social content

## Consequences

**Positive**
- No ToS violations or GDPR minefields in the template.
- Fully reproducible tests and demos.
- Forces the ethics + consent machinery to be exercised even in the default setup.
- Easy to replace the provider later behind a feature flag.

**Negative**
- Less "realistic" signal quality than actual social data (by design).

## Alternatives Considered

- User-uploaded social exports (still requires heavy consent, minimization, retention, and deletion logic).
- Live OAuth scraping (forbidden by most platforms, massive liability).

## References

- `app/services/recommender.py`
- `docs/concepts/synthetic-data.md` (to be written)
- Ethics policy checks around `has_consent_for_social`
