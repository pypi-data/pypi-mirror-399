"""
Interrupt handling for LangGraph Python SDK.

This package enables:
- Human-in-the-loop (HITL)
- Approval-based pauses
- Escalation
- Safe resume of execution

Interrupts:
- Do NOT mutate state
- Do NOT execute actions
- ONLY control execution flow
"""
