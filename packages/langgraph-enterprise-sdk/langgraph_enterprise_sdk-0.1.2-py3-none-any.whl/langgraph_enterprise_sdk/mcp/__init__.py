"""
Model Context Protocol (MCP) integration layer.

Responsibilities:
- Tool & resource invocation via MCP
- Transport abstraction (HTTP / stdio / WebSocket)
- Schema validation
- Security metadata propagation

MCP:
- Does NOT control execution
- Does NOT mutate agent state
- Is invoked by orchestration nodes
"""
