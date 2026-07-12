# Commit Conventions & Change Policy

This project requires **small, single-purpose commits and PRs** and **structured commit messages**. The goal is to produce a git history that is useful and self-documenting for both humans and AI agents.

## Core Rules

1. **One logical change per commit**
   - Examples of atomic commits:
     - "Add EmployeeAssessment model class"
     - "Extend EthicalPolicy.refuse_unethical_request with protected-class bias rule"
     - "Add career_recommendations GraphQL field + type (types.py only)"
     - "Add 4 STRIDE-AI threats for assessment poisoning + supply chain"
     - "Update README.md quickstart section for federal examples"
   - Never mix unrelated refactors, docs, and features in one commit.

2. **Verify before every commit**
   - Run relevant tests + `uv run python scripts/verify.py` (at minimum the smoke paths for the changed area).
   - Never leave the tree in a broken state for the primary flows.

3. **Small PRs preferred**
   - Open or push small focused PRs frequently.
   - Use descriptive branch names (e.g. `federal/domain-models-assessment`, `federal/ethics-bias-rules`).

## Commit Message Format (Mandatory)

Use this structure for every commit after the policy is introduced:

```
<type>(<scope>): <imperative present-tense summary (≤72 chars)>

Context / Why:
- <one sentence business or plan driver>
- Ties to Phase X of federal pivot plan (or specific user request).

Design decisions:
- <key choice made and rationale>
- Reused <ExistingClass/Function in app/path/to/file.py> because <reason>.
- Followed <invariant e.g. flat GraphQL / Principal threading / ethics-before-business>.

Tradeoffs considered:
- <Alternative A> vs <chosen>: <why we chose the current approach>
- Impact on complexity, performance, compliance, or maintainability.

Changes:
- <bullet list of key files or 1-3 bullets max>

Verification performed:
- `uv run pytest tests/test_xxx.py -q`
- `uv run python scripts/verify.py` (exercised: recommendations, agent bias refusal, MCP with consent 0/2)
- Manual: <specific curl / GraphiQL / MCP call that demonstrates behavior>

Refs:
- plan.md (Phase Y / section Z)
- ADR-00N (if any)
- User query 2026-07-12 (federal pivot, employee lifecycle predictor, small commits policy)
```

### Allowed Types
- `feat`: new capability or domain element
- `fix`: bug or incorrect behavior
- `refactor`: restructure without behavior change
- `docs`: documentation only
- `test`: add or update tests
- `chore`: tooling, config, hygiene
- `sec`: security-related (auth, guardrails, logging)
- `compliance`: FedRAMP, NIST, STRIDE, IL docs or mappings

Scopes should be short and consistent (e.g. `models`, `ethics`, `graphql`, `mcp`, `recommender`, `docs/readme`, `threats/stride`).

## Why This Policy Exists

- The federal pivot involves ethically sensitive, high-stakes changes (career-impacting predictions, bias, consent, classified data handling).
- Future maintainers and agents must be able to understand **why** a decision was made and what tradeoffs were accepted.
- Small commits make reviews, reverts, and `git bisect` effective.
- Structured messages turn the git log into living design documentation.

## Enforcement

- All contributors (including this agent) must follow this starting from the introduction of the policy document.
- During review of this project, `git log --oneline` and full commit bodies will be inspected for adherence.
- Large or poorly documented commits will be rejected or split in follow-up work.

## Related

- See the top-level `plan.md` (federal pivot plan) for the execution approach.
- Update this file when the policy itself evolves (with its own structured commit).
