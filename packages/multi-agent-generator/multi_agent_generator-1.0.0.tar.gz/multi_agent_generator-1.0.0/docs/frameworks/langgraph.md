# LangGraph Framework

LangGraph is LangChain's framework for **stateful, multi-actor applications**.  
It represents workflows as directed graphs with:

- **Nodes**: agents, tools, or operations
- **Edges**: control/data flow
- **Conditions**: define branching behavior

---

## Example

```bash
multi-agent-generator "Build me a LangGraph workflow for customer support" --framework langgraph
```

### Generates a graph like:
```json
{
  "agents": [{ "name": "support_agent", "llm": "gpt-4.1-mini" }],
  "nodes": [
    { "name": "greet_customer", "agent": "support_agent" },
    { "name": "resolve_issue", "agent": "support_agent" }
  ],
  "edges": [
    { "source": "greet_customer", "target": "resolve_issue" }
  ]
}
```