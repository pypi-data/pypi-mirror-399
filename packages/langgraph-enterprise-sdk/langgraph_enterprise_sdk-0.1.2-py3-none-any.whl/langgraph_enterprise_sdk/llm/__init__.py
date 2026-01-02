"""
LLM abstraction layer.

Responsibilities:
- Define a unified LLM interface
- Provide routing, safety, caching, and cost tracking
- Keep vendors as implementation details

LLMs:
- Do NOT control flow
- Do NOT mutate state
- Are invoked by orchestration nodes
"""
