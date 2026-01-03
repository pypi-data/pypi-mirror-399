# CrewAI Flow

CrewAI Flow extends CrewAI with **event-driven workflows**.  
It enables sequential, parallel, and conditional task execution with state management.

---

## Example

```bash
multi-agent-generator "Analyze customer reviews and generate insights" --framework crewai-flow
```

### This produces:
- Specialized agents (e.g., Data Collector, Data Analyst, Writer)

- Sequential flow: collect → analyze → summarize

- Task delegation and transitions defined