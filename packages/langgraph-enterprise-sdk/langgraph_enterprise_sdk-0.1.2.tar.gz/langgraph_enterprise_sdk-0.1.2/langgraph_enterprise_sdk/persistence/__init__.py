"""
Persistence layer for LangGraph Python SDK.

Responsibilities:
- Checkpointing execution state
- Snapshotting for time-travel
- Recovery after failure
- Serialization / deserialization

Persistence:
- Does NOT control execution
- Does NOT mutate state implicitly
"""
