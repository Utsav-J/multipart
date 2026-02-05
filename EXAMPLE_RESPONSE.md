# Example Multi-Part Response

This document shows a concrete example of what the multi-part response looks like when sent and received.

## 📨 Request

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "What is machine learning and how does it work?"
      }
    ]
  }
}
```

## 📬 Response Structure

### A2A Protocol Response

```json
{
  "task": {
    "id": "task-123",
    "contextId": "context-456",
    "state": "completed",
    "artifacts": [
      {
        "artifactId": "qa_response",
        "parts": [
          {
            "kind": "text",
            "text": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. Instead of following pre-programmed rules, ML systems identify patterns in data and make predictions or decisions based on those patterns.\n\nHere's how it works:\n\n1. **Data Collection**: Gather relevant data (e.g., images, text, numbers)\n2. **Training**: Feed data to algorithms that identify patterns\n3. **Model Creation**: The algorithm creates a mathematical model of the patterns\n4. **Prediction**: Use the model to make predictions on new, unseen data\n5. **Refinement**: Continuously improve the model with more data\n\nCommon applications include image recognition, natural language processing, recommendation systems, and predictive analytics. The key advantage is that ML systems can improve their performance over time as they process more data."
          },
          {
            "kind": "data",
            "data": {
              "follow_up_questions": [
                "What's the difference between supervised and unsupervised learning?",
                "How do neural networks fit into machine learning?",
                "What are some real-world examples of machine learning in everyday life?",
                "What skills do I need to get started with machine learning?"
              ],
              "confidence": 0.95,
              "topics": [
                "machine learning",
                "artificial intelligence",
                "data science",
                "algorithms",
                "pattern recognition"
              ]
            }
          }
        ]
      }
    ]
  }
}
```

## 🔍 Breaking Down the Parts

### Part 1: TextPart (The Answer)

This is what users see as the main response:

```
Machine learning is a subset of artificial intelligence that enables 
computers to learn from data without being explicitly programmed...

[Full answer text continues...]
```

**Properties:**
- `kind: "text"`
- `text: <string>` - The answer content
- Human-readable
- Can be rendered as markdown or plain text
- Contains the comprehensive answer

### Part 2: DataPart (Follow-ups & Metadata)

This is structured data for programmatic use:

```json
{
  "follow_up_questions": [
    "What's the difference between supervised and unsupervised learning?",
    "How do neural networks fit into machine learning?",
    "What are some real-world examples of machine learning in everyday life?",
    "What skills do I need to get started with machine learning?"
  ],
  "confidence": 0.95,
  "topics": [
    "machine learning",
    "artificial intelligence",
    "data science",
    "algorithms",
    "pattern recognition"
  ]
}
```

**Properties:**
- `kind: "data"`
- `data: <object>` - Structured JSON object
- Machine-readable
- Can be parsed and used in UI
- Contains metadata and follow-ups

## 🎨 How Clients Can Use This

### 1. Display the Answer

```python
# Extract TextPart
text_part = response.artifacts[0].parts[0]
print(text_part.text)

# Or in a web UI:
# <div class="answer">{text_part.text}</div>
```

### 2. Render Follow-up Questions as Buttons

```python
# Extract DataPart
data_part = response.artifacts[0].parts[1]
follow_ups = data_part.data['follow_up_questions']

for question in follow_ups:
    print(f"[{question}]")  # Render as clickable button
```

**UI Example:**
```
┌─────────────────────────────────────────────────────────────┐
│ Machine learning is a subset of artificial intelligence... │
│                                                             │
│ [Full answer continues...]                                 │
└─────────────────────────────────────────────────────────────┘

📊 Confidence: 95%

🔮 Continue the conversation:
┌────────────────────────────────────────────────────────────┐
│ [What's the difference between supervised/unsupervised?]   │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ [How do neural networks fit into machine learning?]        │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ [Real-world examples in everyday life?]                    │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ [Skills needed to get started?]                            │
└────────────────────────────────────────────────────────────┘

🏷️  Topics: machine learning · AI · data science · algorithms
```

### 3. Show Confidence Indicator

```python
confidence = data_part.data['confidence']
confidence_pct = confidence * 100
print(f"Confidence: {confidence_pct}%")

# Or visual indicator:
# ████████████████████░  95%
```

### 4. Enable Topic Navigation

```python
topics = data_part.data['topics']
print(f"Related topics: {', '.join(topics)}")

# Render as clickable tags:
# [machine learning] [AI] [data science] [algorithms]
```

## 💻 Code Example: Creating This Response

### In agent_executor.py

```python
async def execute(self, context: RequestContext, event_queue: EventQueue):
    # Get user's question
    question = context.get_user_input()
    
    # Get task
    task = context.current_task or new_task(context.message)
    updater = TaskUpdater(event_queue, task.id, task.context_id)
    
    # Get answer from agent (which uses the system prompt)
    response = await self.agent.get_response(question)
    
    # ===== CREATE MULTI-PART RESPONSE =====
    parts = [
        # Part 1: The answer (TextPart)
        Part(root=TextPart(text=response['answer_text'])),
        
        # Part 2: Follow-ups and metadata (DataPart)
        Part(root=DataPart(data={
            'follow_up_questions': response['follow_up_questions'],
            'confidence': response['confidence'],
            'topics': response['topics'],
        })),
    ]
    
    # Send multi-part artifact
    await updater.add_artifact(parts, name='qa_response')
    await updater.complete()
```

## 📊 Comparison: Single vs Multi-Part

### ❌ Single-Part Response (Plain Text Only)

```json
{
  "parts": [
    {
      "kind": "text",
      "text": "Machine learning is...\n\nFollow-up questions:\n1. What's the difference...\n2. How do neural networks...\n\nConfidence: 95%\nTopics: ML, AI, data science"
    }
  ]
}
```

**Problems:**
- Follow-ups are plain text (not interactive)
- Must parse text to extract structured data
- Can't easily render as UI elements
- Mixing presentation and data

### ✅ Multi-Part Response (Text + Data)

```json
{
  "parts": [
    {
      "kind": "text",
      "text": "Machine learning is..."
    },
    {
      "kind": "data",
      "data": {
        "follow_up_questions": [...],
        "confidence": 0.95,
        "topics": [...]
      }
    }
  ]
}
```

**Benefits:**
- Structured data ready for UI
- Follow-ups can be clickable buttons
- Confidence can be a progress bar
- Topics can be navigation tags
- Clean separation of concerns

## 🔗 Real-World Use Cases

### Use Case 1: Customer Support Bot

**TextPart:** Answer to support question
**DataPart:**
```json
{
  "follow_up_questions": ["How do I...?", "What about...?"],
  "related_articles": [{"title": "...", "url": "..."}],
  "escalation_needed": false,
  "category": "billing"
}
```

### Use Case 2: Educational Assistant

**TextPart:** Explanation of concept
**DataPart:**
```json
{
  "follow_up_questions": ["Practice question 1?", "Practice question 2?"],
  "difficulty_level": "intermediate",
  "prerequisites": ["concept1", "concept2"],
  "resources": [{"title": "Video tutorial", "url": "..."}]
}
```

### Use Case 3: Code Assistant

**TextPart:** Code explanation
**DataPart:**
```json
{
  "follow_up_questions": ["How to optimize?", "Handle edge cases?"],
  "code_snippet": "def example(): ...",
  "language": "python",
  "complexity": "O(n)",
  "best_practices": ["Use list comprehension", "Add error handling"]
}
```

## 📝 Summary

**Multi-part responses enable:**

1. ✅ Better UX - Separate presentation from data
2. ✅ Interactive UI - Render follow-ups as buttons
3. ✅ Rich metadata - Confidence, topics, citations
4. ✅ Programmatic access - Parse data without text parsing
5. ✅ Flexibility - Add more parts as needed

**Key Pattern:**
```python
parts = [
    Part(root=TextPart(text=answer)),      # Human-readable
    Part(root=DataPart(data=metadata)),     # Machine-readable
]
await updater.add_artifact(parts)
```

See the complete implementation in `agent_executor.py`!
