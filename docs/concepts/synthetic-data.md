# Synthetic Data Only

## Decision

All "social" signals in customer-spend-microservice are **synthetic and versioned**. There is no support for ingesting real social media data.

See `app/services/recommender.py`:
```python
SYNTHETIC_PROFILES = {
    "demo-user-123": ["coffee", "tech gadgets", "travel", "fitness"],
    ...
}
```

## Why This Choice?

Real social data introduces severe risks:
- Privacy and consent (GDPR, CCPA, etc.)
- Terms of Service violations from platforms
- Bias, accuracy, and ethical problems
- Legal liability for a reference template

By using synthetic data:
- The ethics and consent machinery is exercised even in the default demo.
- Everything is reproducible and deterministic for tests.
- We demonstrate **source attribution** clearly (`"synthetic_social"` appears in `dataSources` only when consent is granted).
- It is trivial for adopters to replace the provider with real (properly consented) data behind a feature flag.

## How It Works

1. `recommender.py` looks up interests by `user_id` from the synthetic map.
2. If `principal.has_consent_for_social()` and `enable_synthetic_social` is true → include `"synthetic_social"` in sources.
3. `EthicalPolicy.evaluate_recommendation` enforces the consent check.
4. Recommendations and agent responses always declare the sources used.

## Consent Interaction

- `consent_level >= 2` (or `require_consent_for_social=false`) allows synthetic social.
- Lower consent → sources limited to `"questionnaire"`.
- The recommender still returns useful (but more conservative) suggestions.

See [Ethics & Consent](ethics-and-consent.md) and [Principal Model](principal-model.md).

## Extending / Replacing

To use real data:
- Implement a `SocialProvider` interface.
- Gate behind a feature flag + explicit consent record.
- Update `EthicalDecisionLog` classification to `SENSITIVE_INFERENCE`.
- Add proper retention, deletion, and audit flows.

The template makes the replacement point obvious because attribution and consent checks are already in place.

## Verification

`scripts/verify.py` and tests in `test_mcp.py` / `test_recommender` (implicit) exercise both consent paths.

Run with different tokens to see the difference in `dataSources` and `ethical_note`.

## References

- `app/services/recommender.py`
- `app/core/ethics.py` (check_consent_for_social, evaluate_recommendation)
- ADR-002 in `docs/ADRs/`