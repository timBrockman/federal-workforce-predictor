# Recipe: Replace the Agent Simulation with Real Pydantic AI

## Current State

`app/services/agent.py` currently does:

```python
# For template we simulate with rules + recs call
recs, rec_decision = get_recommendations(...)
```

This is intentional for determinism and zero LLM cost in the reference.

## Steps to Make It Real

1. **Ensure dependencies**

`pydantic-ai` and a provider (via LiteLLM or native) are already in pyproject.

2. **Implement a real agent**

Use Pydantic AI's `Agent` with tools that call your existing services (passing the `Principal`).

Example skeleton:

```python
from pydantic_ai import Agent
from pydantic_ai.models.litellm import LiteLLMModel

agent = Agent(
    model=LiteLLMModel(model_name=settings.llm_model),
    tools=[...],  # your safe tools
    system_prompt=ETHICS_SYSTEM_PROMPT,
)

async def ask_budget_agent(principal, question):
    # pre-filter with EthicalPolicy
    ...
    result = await agent.run(question, deps=principal)
    # post-process, log decision, persist
    ...
```

3. **Guardrails**

- Keep the pre-filter refusal.
- Make tools themselves check consent / ethics where relevant.
- Log the final `EthicalDecision`.

4. **Configuration**

Users change `LLM_MODEL`. You may want to add `AGENT_ENABLED` or similar.

5. **Testing**

- Keep the simulation path for fast tests.
- Add a `pytest.mark.slow` or `live` test that actually calls the LLM (guarded by env).
- Or use Pydantic AI's test utilities / recorded responses.

6. **Docs**

Update:
- `docs/concepts/` if needed
- `docs/extending/swapping-the-agent.md` (this file)
- Mention in use-cases and productionizing.

## Tips

- Use structured output models for the agent's final answer.
- Inject the `Principal` as deps so tools can use it.
- Be explicit about which tools are exposed (same curated philosophy as MCP).

This is one of the most valuable "next steps" for people adopting the template.