# CrewAI Framework

CrewAI orchestrates **role-playing autonomous AI agents**.  
Each agent has:

- **Role**: what they do
- **Goal**: their objective
- **Backstory**: context
- **Tools**: available abilities

Tasks are assigned to agents with expected outputs.

---

## Example

```bash
multi-agent-generator "Research AI trends and write a summary" --framework crewai
```

### Produces agents like:
```json
{
  "agents": [
    {
      "name": "research_specialist",
      "role": "Research Specialist",
      "goal": "Gather AI research trends",
      "tools": ["search_tool"]
    },
    {
      "name": "writer",
      "role": "Content Writer",
      "goal": "Write a summary",
      "tools": ["editor_tool"]
    }
  ],
  "tasks": [...]
}
```