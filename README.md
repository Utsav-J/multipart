# QA Agent with Follow-up Questions

This example demonstrates how to build an A2A agent that returns **multi-part responses** containing both text and structured data.

## 🎯 What This Example Shows

- **Well-designed system prompt**: Instructions for generating both answers and follow-up questions
- **Multi-part response pattern**: Returning both `TextPart` (answer) and `DataPart` (follow-ups)
- **Structured output**: Using Pydantic models to ensure consistent response format
- **LangGraph integration**: Building agents with state management

## 📋 Response Structure

When you ask a question, the agent returns a response with **two parts**:

### Part 1: TextPart (Human-readable answer)
```
The comprehensive answer to your question, formatted in clear prose...
```

### Part 2: DataPart (Structured follow-up data)
```json
{
  "follow_up_questions": [
    "How does X relate to Y?",
    "What are the practical applications of Z?",
    "Can you explain more about W?"
  ],
  "confidence": 0.95,
  "topics": ["topic1", "topic2", "topic3"]
}
```

## 🚀 How It Works

### 1. System Prompt (`agent.py`)

The system prompt clearly instructs the LLM to:
- Generate a comprehensive answer
- Create 3-5 relevant follow-up questions
- Assess confidence and identify topics

```python
SYSTEM_INSTRUCTION = """You are a knowledgeable AI assistant...

Your task is to:
1. Provide a clear, accurate answer
2. Generate 3-5 relevant follow-up questions
3. Assess your confidence
4. Identify key topics covered
..."""
```

### 2. Structured Response Model

A Pydantic model ensures consistent output:

```python
class AnswerWithFollowups(BaseModel):
    answer: str
    follow_up_questions: list[str]
    confidence: float
    topics: list[str]
```

### 3. Multi-Part Response (`agent_executor.py`)

The key pattern for sending multi-part responses:

```python
# Create multi-part response
parts = [
    # Part 1: Text answer
    Part(root=TextPart(text=answer_text)),
    
    # Part 2: Structured follow-ups
    Part(root=DataPart(data=follow_up_data)),
]

# Send both parts together
await updater.add_artifact(parts, name='qa_response')
```

## 📦 Installation

```bash
cd agents/qa_with_followups
uv sync
```

## 🏃 Running the Agent

```bash
# Set your API key
export GOOGLE_API_KEY="your-api-key"

# Run the agent
uv run python __main__.py
```

The agent will start on `http://localhost:9998`

## 🧪 Testing the Agent

### Using the A2A CLI client:

```bash
# From the samples/python directory
cd hosts/cli

# Send a question
uv run python __main__.py \
  --agent-url http://localhost:9998/a2a/v1 \
  --prompt "What is quantum computing?"
```

### Expected Response:

You'll receive a response with two parts:

1. **TextPart**: A detailed explanation of quantum computing
2. **DataPart**: Structured JSON with:
   - 3-5 follow-up questions
   - Confidence score
   - Key topics covered

## 🔧 Customization

### Change the LLM Model

```bash
# Use OpenAI instead of Google
export MODEL_SOURCE=openai
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o"
```

### Modify the System Prompt

Edit `agent.py` to customize:
- How answers are structured
- Number of follow-up questions (currently 3-5)
- What metadata to include

### Add Tools

You can add LangChain tools to the agent:

```python
from langchain_core.tools import tool

@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base."""
    ...

self.graph = create_react_agent(
    self.model,
    tools=[search_knowledge_base],  # Add your tools
    ...
)
```

## 🎓 Key Concepts

### Multi-Part Responses

A2A supports multiple content types in a single response:

- **TextPart**: Human-readable text
- **DataPart**: Structured JSON data
- **FilePart**: File attachments

You can combine these in a single `add_artifact` call.

### Why Use Multi-Part?

1. **Better UX**: Display text naturally while using data programmatically
2. **Structured Data**: Enable downstream processing without parsing text
3. **Rich Metadata**: Provide confidence scores, citations, follow-ups, etc.
4. **Separation of Concerns**: Keep presentation and data separate

## 📚 Related Examples

- **adk_expense_reimbursement**: Another multi-part response example
- **langgraph**: Basic LangGraph agent structure
- **helloworld**: Simplest A2A agent example

## 🐛 Troubleshooting

### Agent returns single-part response

Make sure you're using `add_artifact` with a list of `Part` objects:

```python
# ✅ Correct
parts = [Part(root=TextPart(...)), Part(root=DataPart(...))]
await updater.add_artifact(parts)

# ❌ Wrong - only sends text
await event_queue.enqueue_event(new_agent_text_message(...))
```

### Follow-up questions are generic

Improve your system prompt with more specific guidance about what makes good follow-up questions for your domain.

## 📄 License

Apache 2.0 - See the repository LICENSE file.
