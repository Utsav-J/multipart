# Multi-Part Response Quick Reference

## 🚀 Quick Start (5 Minutes)

### Step 1: Define Pydantic Model

```python
from pydantic import BaseModel, Field

class AnswerWithFollowups(BaseModel):
    answer: str
    follow_up_questions: list[str] = Field(min_items=3, max_items=5)
    confidence: float = Field(ge=0.0, le=1.0)
    topics: list[str]
```

### Step 2: Create System Prompt

```python
SYSTEM_INSTRUCTION = """You are an AI assistant.

Generate:
1. A comprehensive answer
2. 3-5 relevant follow-up questions
3. Confidence score (0.0-1.0)
4. Key topics covered
"""
```

### Step 3: Build Agent with LangGraph

```python
from langgraph.prebuilt import create_react_agent

graph = create_react_agent(
    model=your_model,
    tools=[],
    prompt=SYSTEM_INSTRUCTION,
    response_format=(FORMAT_INSTRUCTION, AnswerWithFollowups),
)
```

### Step 4: Send Multi-Part Response

```python
from a2a.types import Part, TextPart, DataPart

# In your agent_executor.py execute() method:
parts = [
    Part(root=TextPart(text=answer_text)),
    Part(root=DataPart(data=follow_up_data)),
]
await updater.add_artifact(parts)
await updater.complete()
```

## 📋 Core Imports

```python
# A2A types
from a2a.types import (
    DataPart,         # For structured data
    Part,             # Wrapper for all part types
    TextPart,         # For text content
)

# Agent execution
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

# Utilities
from a2a.utils import new_task

# Pydantic for structured output
from pydantic import BaseModel, Field
```

## 🎯 The Pattern

### Basic Multi-Part Pattern

```python
# Create parts
parts = [
    Part(root=TextPart(text="Your answer here")),
    Part(root=DataPart(data={"key": "value"})),
]

# Send
await updater.add_artifact(parts, name='optional_name')
await updater.complete()
```

### Full Execute Method

```python
async def execute(self, context: RequestContext, event_queue: EventQueue):
    # 1. Get input
    query = context.get_user_input()
    
    # 2. Get/create task
    task = context.current_task
    if not task:
        task = new_task(context.message)
        await event_queue.enqueue_event(task)
    
    # 3. Create updater
    updater = TaskUpdater(event_queue, task.id, task.context_id)
    
    # 4. Get response from agent
    response = await self.agent.get_response(query)
    
    # 5. Create multi-part response
    parts = [
        Part(root=TextPart(text=response['answer'])),
        Part(root=DataPart(data=response['metadata'])),
    ]
    
    # 6. Send
    await updater.add_artifact(parts)
    await updater.complete()
```

## 📦 Part Types

### TextPart
```python
Part(root=TextPart(text="String content here"))
```
- Human-readable text
- Rendered naturally in UIs
- Main answer/explanation

### DataPart
```python
Part(root=DataPart(data={
    "follow_up_questions": ["Q1?", "Q2?"],
    "confidence": 0.95,
    "any_key": "any_value"
}))
```
- Structured JSON data
- Machine-readable
- Metadata, follow-ups, etc.

### FilePart (Optional)
```python
Part(root=FilePart(
    file=FileWithUri(uri="...", mime_type="...")
))
```
- File attachments
- Images, PDFs, etc.

## 🎨 Response Data Structures

### Minimal Structure
```python
data = {
    "follow_up_questions": ["Q1?", "Q2?", "Q3?"]
}
```

### Standard Structure
```python
data = {
    "follow_up_questions": ["Q1?", "Q2?", "Q3?"],
    "confidence": 0.92,
    "topics": ["topic1", "topic2"]
}
```

### Rich Structure
```python
data = {
    "follow_up_questions": [
        {"question": "Q1?", "difficulty": "easy"},
        {"question": "Q2?", "difficulty": "medium"}
    ],
    "confidence": 0.92,
    "topics": ["topic1", "topic2"],
    "metadata": {
        "response_time_ms": 1234,
        "model_version": "1.0.0",
        "sources": ["source1", "source2"]
    }
}
```

## 🔧 Common Patterns

### Pattern 1: Answer + Follow-ups
```python
parts = [
    Part(root=TextPart(text=answer)),
    Part(root=DataPart(data={"follow_up_questions": [...]})),
]
```

### Pattern 2: Summary + Details
```python
parts = [
    Part(root=TextPart(text=summary)),
    Part(root=DataPart(data=detailed_analysis)),
]
```

### Pattern 3: Multiple Data Parts
```python
parts = [
    Part(root=TextPart(text=answer)),
    Part(root=DataPart(data={"confidence": 0.95})),
    Part(root=DataPart(data={"follow_ups": [...]})),
]
```

### Pattern 4: Text + File + Data
```python
parts = [
    Part(root=TextPart(text="See attached chart")),
    Part(root=FilePart(file=chart_file)),
    Part(root=DataPart(data={"data_points": [...]})),
]
```

## ⚠️ Common Mistakes

### ❌ Wrong: Missing Part wrapper
```python
parts = [
    TextPart(text="answer"),  # Missing Part()
    DataPart(data={})         # Missing Part()
]
```

### ✅ Correct: With Part wrapper
```python
parts = [
    Part(root=TextPart(text="answer")),
    Part(root=DataPart(data={}))
]
```

### ❌ Wrong: Sending only text message
```python
# This sends only text, not multi-part
await event_queue.enqueue_event(
    new_agent_text_message("answer")
)
```

### ✅ Correct: Using add_artifact
```python
# This sends multi-part
await updater.add_artifact(parts)
```

### ❌ Wrong: Forgot to complete
```python
await updater.add_artifact(parts)
# Missing: await updater.complete()
```

### ✅ Correct: Complete the task
```python
await updater.add_artifact(parts)
await updater.complete()
```

## 🧪 Testing

### Test Client Example
```python
from a2a.utils import a2a_grpc_client
from a2a.types import Message, Part, TextPart

async with a2a_grpc_client(agent_url) as client:
    message = Message(
        role='user',
        parts=[Part(root=TextPart(text="Your question"))]
    )
    task = await client.message_send(new_message=message)
    
    # Access parts
    for artifact in task.artifacts:
        for part in artifact.parts:
            if isinstance(part.root, TextPart):
                print("Answer:", part.root.text)
            elif hasattr(part.root, 'data'):
                print("Data:", part.root.data)
```

## 📚 File Reference

| File | Purpose |
|------|---------|
| `agent.py` | System prompt + LangGraph agent |
| `agent_executor.py` | Multi-part response implementation |
| `__main__.py` | Server setup |
| `simple_example.py` | Minimal example without LangGraph |
| `test_client.py` | Test client for the agent |
| `SYSTEM_PROMPT_GUIDE.md` | Detailed system prompt guide |
| `EXAMPLE_RESPONSE.md` | Complete response examples |

## 🎓 Key Concepts

1. **TextPart** = Human-readable content
2. **DataPart** = Machine-readable structure
3. **Part** = Wrapper for TextPart/DataPart/FilePart
4. **add_artifact()** = Send multi-part response
5. **System Prompt** = Instructs LLM what to generate
6. **Pydantic Model** = Enforces structured output

## 💡 Pro Tips

1. ✅ Always wrap TextPart/DataPart in Part()
2. ✅ Use descriptive names for artifacts
3. ✅ Include confidence scores for trust
4. ✅ Generate 3-5 follow-ups (not too many)
5. ✅ Test with various question types
6. ✅ Handle missing data gracefully
7. ✅ Use Pydantic constraints (min_items, max_items)
8. ✅ Complete task after adding artifact

## 🚦 Checklist

- [ ] Defined Pydantic model
- [ ] Created system prompt
- [ ] Integrated with LangGraph
- [ ] Extract answer and data
- [ ] Create multi-part response
- [ ] Wrap in Part()
- [ ] Send with add_artifact()
- [ ] Complete task
- [ ] Test with client

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Only getting text | Use `add_artifact(parts)` not `new_agent_text_message()` |
| Missing Part wrapper | Wrap TextPart/DataPart in `Part(root=...)` |
| Task never completes | Add `await updater.complete()` |
| No structured output | Check Pydantic model and response_format |
| Follow-ups are generic | Improve system prompt instructions |

## 🔗 Resources

- Full example: See all files in this directory
- A2A docs: https://google.github.io/A2A/
- LangGraph docs: https://langchain-ai.github.io/langgraph/
