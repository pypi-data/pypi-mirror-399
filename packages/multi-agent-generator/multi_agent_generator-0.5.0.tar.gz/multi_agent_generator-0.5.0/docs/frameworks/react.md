# ReAct (Classic)

ReAct (Reasoning + Acting) combines **thoughts + actions**.  
The agent reasons about a problem, then decides when to call a tool.

---

## Example

```bash
multi-agent-generator "Answer math questions using a calculator tool" --framework react
```

### Produces:

- An agent with reasoning + acting steps

- Tool definitions with parameters

- ReAct-style execution loop