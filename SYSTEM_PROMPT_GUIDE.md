# System Prompt Design for Multi-Part Responses

This guide shows how to design a system prompt that instructs the LLM to generate both answers and follow-up questions, then structure them into multi-part responses.

## 🎯 The Goal

Create an agent where:
1. **System prompt** tells the LLM to generate answer + follow-ups
2. **TextPart** contains the actual answer
3. **DataPart** contains structured follow-up questions

## 📝 System Prompt Design

### Well-Designed System Prompt

```python
SYSTEM_INSTRUCTION = """You are a knowledgeable and helpful AI assistant.

Your task is to:
1. Provide a clear, accurate answer to the user's question
2. Generate 3-5 relevant follow-up questions
3. Assess your confidence in the answer
4. Identify key topics covered

ANSWER GUIDELINES:
- Be thorough but concise
- Use clear language and structure
- Cite specific facts when possible
- If uncertain, reflect it in confidence score

FOLLOW-UP QUESTION GUIDELINES:
- Generate questions that naturally extend from the topic
- Make questions specific and actionable
- Vary question types (deeper dive, related topics, applications)
- Ensure relevance to user's interests

RESPONSE FORMAT:
Your response will be structured into:
1. A text part containing your answer
2. A data part containing follow-up questions, confidence, and topics
"""
```

### Response Format Instruction

```python
FORMAT_INSTRUCTION = """Structure your response with:
- answer: Your comprehensive answer
- follow_up_questions: Exactly 3-5 contextual follow-up questions
- confidence: Your confidence level (0.0 to 1.0)
- topics: List of key topics covered
"""
```

## 🏗️ Pydantic Model for Structured Output

Define the exact structure you want from the LLM:

```python
from pydantic import BaseModel, Field

class AnswerWithFollowups(BaseModel):
    """Response format containing answer and follow-up questions."""
    
    answer: str = Field(
        description="The comprehensive answer to the user's question"
    )
    
    follow_up_questions: list[str] = Field(
        description="3-5 relevant follow-up questions",
        min_items=3,
        max_items=5,
    )
    
    confidence: float = Field(
        description="Confidence level (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    
    topics: list[str] = Field(
        description="Key topics covered in the answer"
    )
```

## 🔄 Integration with LangGraph

### Creating the Agent

```python
from langgraph.prebuilt import create_react_agent

graph = create_react_agent(
    model=your_llm_model,
    tools=[],  # Add tools if needed
    checkpointer=memory,
    prompt=SYSTEM_INSTRUCTION,  # System prompt here
    response_format=(FORMAT_INSTRUCTION, AnswerWithFollowups),  # Structured output
)
```

### Getting the Structured Response

```python
def get_agent_response(self, config):
    """Extract structured response from agent state."""
    current_state = self.graph.get_state(config)
    structured_response = current_state.values.get('structured_response')
    
    if isinstance(structured_response, AnswerWithFollowups):
        return {
            'answer_text': structured_response.answer,
            'follow_up_data': {
                'follow_up_questions': structured_response.follow_up_questions,
                'confidence': structured_response.confidence,
                'topics': structured_response.topics,
            }
        }
```

## 📤 Creating Multi-Part Response

### The Key Pattern

```python
async def execute(self, context: RequestContext, event_queue: EventQueue):
    # ... setup code ...
    
    # Get response from agent (uses system prompt)
    response = await self.agent.get_response(query)
    
    # Extract answer and follow-up data
    answer_text = response['answer_text']
    follow_up_data = response['follow_up_data']
    
    # ===== CREATE MULTI-PART RESPONSE =====
    parts = [
        # Part 1: TextPart - The actual answer
        Part(root=TextPart(text=answer_text)),
        
        # Part 2: DataPart - Structured follow-ups
        Part(root=DataPart(data=follow_up_data)),
    ]
    
    # Send both parts together
    await updater.add_artifact(parts, name='qa_response')
    await updater.complete()
```

## 📊 Complete Flow Diagram

```
User Question
     ↓
┌─────────────────────────────────────────────┐
│ System Prompt                               │
│ - Instructions for answer format            │
│ - Instructions for follow-up generation     │
│ - Quality guidelines                        │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│ LLM Processing                              │
│ - Generates comprehensive answer            │
│ - Creates 3-5 follow-up questions          │
│ - Assesses confidence                       │
│ - Identifies topics                         │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│ Structured Response (Pydantic Model)        │
│ {                                           │
│   answer: "...",                            │
│   follow_up_questions: [...],               │
│   confidence: 0.95,                         │
│   topics: [...]                             │
│ }                                           │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│ Agent Executor                              │
│ Splits response into two parts:             │
│                                             │
│ Part 1: TextPart                            │
│   └─ answer text                            │
│                                             │
│ Part 2: DataPart                            │
│   └─ {follow_up_questions, confidence, ...} │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│ A2A Response                                │
│ artifacts: [                                │
│   {                                         │
│     parts: [                                │
│       {type: "text", text: "..."},          │
│       {type: "data", data: {...}}           │
│     ]                                       │
│   }                                         │
│ ]                                           │
└─────────────────────────────────────────────┘
```

## 💡 Example Interaction

### Input
```
"What is quantum computing?"
```

### System Prompt Processing
The LLM receives your system prompt and generates a structured response:

```python
{
    "answer": "Quantum computing is a revolutionary technology that leverages...",
    "follow_up_questions": [
        "How do quantum computers differ from classical computers?",
        "What are the main applications of quantum computing?",
        "What challenges remain in building practical quantum computers?"
    ],
    "confidence": 0.92,
    "topics": ["quantum computing", "qubits", "superposition"]
}
```

### Multi-Part Response Sent

**Part 1 (TextPart):**
```
Quantum computing is a revolutionary technology that leverages 
quantum mechanical phenomena to process information...
```

**Part 2 (DataPart):**
```json
{
  "follow_up_questions": [
    "How do quantum computers differ from classical computers?",
    "What are the main applications of quantum computing?",
    "What challenges remain in building practical quantum computers?"
  ],
  "confidence": 0.92,
  "topics": ["quantum computing", "qubits", "superposition"]
}
```

## 🎨 Client-Side Benefits

With multi-part responses, clients can:

1. **Display the answer naturally as text**
   ```
   TextPart → Render as markdown or plain text
   ```

2. **Create interactive UI from follow-ups**
   ```
   DataPart → Render as clickable buttons/cards:
   
   [How do quantum computers differ?]  [Main applications?]  [Challenges?]
   ```

3. **Show confidence indicators**
   ```
   DataPart.confidence → Progress bar or badge: 92% confidence
   ```

4. **Enable topic-based navigation**
   ```
   DataPart.topics → Tags: [quantum computing] [qubits] [superposition]
   ```

## 🔧 Customization Examples

### Example 1: Citation-Aware Agent

```python
class AnswerWithCitations(BaseModel):
    answer: str
    citations: list[dict[str, str]]  # [{"source": "...", "url": "..."}]
    follow_up_questions: list[str]

# System prompt addition:
"""
Always cite your sources. For each fact, provide:
- source: Name of the source
- url: Link to the source (if available)
"""
```

### Example 2: Difficulty-Aware Agent

```python
class AnswerWithDifficulty(BaseModel):
    answer: str
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    follow_up_questions: list[dict[str, str]]  # [{"question": "...", "difficulty": "..."}]

# System prompt addition:
"""
Assess the difficulty level of your answer.
Generate follow-up questions with varied difficulty levels.
"""
```

### Example 3: Multi-Language Agent

```python
class MultilingualAnswer(BaseModel):
    answer: str
    detected_language: str
    follow_up_questions: list[str]
    alternative_phrasings: list[str]

# System prompt addition:
"""
Detect the user's language and respond in the same language.
Provide follow-up questions in the same language.
"""
```

## ✅ Best Practices

1. **Clear Instructions**: Be explicit about what you want in each field
2. **Field Descriptions**: Use Pydantic Field descriptions to guide the LLM
3. **Constraints**: Use min_items, max_items, ge, le to enforce limits
4. **Examples**: Include examples in your system prompt
5. **Fallbacks**: Handle cases where structured response fails
6. **Testing**: Test with edge cases (ambiguous questions, errors, etc.)

## 🚀 Quick Start Checklist

- [ ] Define your system prompt with clear instructions
- [ ] Create Pydantic model for structured output
- [ ] Integrate with LangGraph using response_format
- [ ] Extract answer text and follow-up data
- [ ] Create multi-part response with TextPart + DataPart
- [ ] Send using updater.add_artifact(parts)
- [ ] Test with various questions

## 📚 Further Reading

- See `agent.py` for complete system prompt
- See `agent_executor.py` for multi-part response implementation
- See `simple_example.py` for minimal pattern without LangGraph
- See `test_client.py` for how to consume multi-part responses
