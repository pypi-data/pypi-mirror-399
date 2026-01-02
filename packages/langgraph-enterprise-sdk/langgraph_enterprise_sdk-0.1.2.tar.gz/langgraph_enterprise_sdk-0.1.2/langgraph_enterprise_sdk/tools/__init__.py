"""
Tools layer for LangGraph Python SDK.

Responsibilities:
- Define executable tools
- Enforce sandboxing
- Register and discover tools
- Provide adapters for orchestration layers

Tools:
- Are the ONLY place side effects are allowed
- Must be explicitly registered
- Must be sandboxed
"""
