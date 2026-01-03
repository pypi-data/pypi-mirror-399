# ReAct (LCEL)

ReAct (Reasoning + Acting) with **LangChain Expression Language (LCEL)**.  
Supports **multi-step reasoning**, tool usage, and history tracking.

---

## Example

```bash
multi-agent-generator "Find AI papers and summarize them" --framework react-lcel
```

### Generated agent includes:

- Multi-step reasoning traces

- Tool calls with inputs/outputs

- LangChain Expression Language chain

## Example Snippet
```python
chain = (
    {"input": RunnablePassthrough(), "history": RunnablePassthrough()}
    | react_prompt
    | llm
    | StrOutputParser()
)
```