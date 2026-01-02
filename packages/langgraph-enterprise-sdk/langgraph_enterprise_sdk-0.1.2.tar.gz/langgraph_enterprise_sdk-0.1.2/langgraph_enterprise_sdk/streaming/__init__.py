"""
Streaming layer for LangGraph Python SDK.

Responsibilities:
- Event emission
- Callback hooks
- Transport abstraction (SSE, WebSocket, Kafka, etc.)

Streaming:
- Does NOT control execution
- Does NOT mutate state
- Is optional and non-blocking
"""
