"""
Security layer for LangGraph Python SDK.

Responsibilities:
- Authentication (AuthN)
- Authorization (AuthZ)
- RBAC
- Policy enforcement
- Tenant & agent isolation
- Secrets management

Security:
- Does NOT execute business logic
- Does NOT mutate state
- Is enforced BEFORE execution
"""
