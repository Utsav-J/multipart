"""QA Agent with Follow-up Questions.

This agent answers questions and generates contextual follow-up questions,
returning both as separate parts in the response.
"""

import os
from collections.abc import AsyncIterable
from typing import Any

from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


memory = MemorySaver()


class AnswerWithFollowups(BaseModel):
    """Response format containing answer and follow-up questions."""

    answer: str = Field(description="The comprehensive answer to the user's question")
    follow_up_questions: list[str] = Field(
        description="A list of 3-5 relevant follow-up questions the user might want to ask next",
        min_items=3,
        max_items=5,
    )
    confidence: float = Field(
        description="Confidence level in the answer (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    topics: list[str] = Field(description="Key topics covered in the answer")


class QAWithFollowupsAgent:
    """QA Agent that generates answers with structured follow-up questions."""

    # Well-designed system prompt with clear instructions
    SYSTEM_INSTRUCTION = """You are a knowledgeable and helpful AI assistant that provides comprehensive answers to user questions.

Your task is to:
1. Provide a clear, accurate, and well-structured answer to the user's question
2. Generate 3-5 relevant follow-up questions that the user might want to explore next
3. Assess your confidence in the answer
4. Identify the key topics covered

ANSWER GUIDELINES:
- Be thorough but concise
- Use clear language and structure your response with paragraphs
- Cite specific facts when possible
- If you're uncertain, acknowledge it in your confidence score

FOLLOW-UP QUESTION GUIDELINES:
- Generate questions that naturally extend from the current topic
- Make questions specific and actionable
- Vary the types of questions (e.g., deeper dive, related topics, practical applications)
- Ensure questions are relevant to the user's likely interests

RESPONSE FORMAT:
Your response will be automatically structured into:
1. A text part containing your answer
2. A data part containing follow-up questions, confidence, and topics

Always provide high-quality follow-up questions that add value to the conversation."""

    FORMAT_INSTRUCTION = """Structure your response with:
- answer: Your comprehensive answer to the question
- follow_up_questions: Exactly 3-5 contextual follow-up questions
- confidence: Your confidence level (0.0 to 1.0)
- topics: List of key topics covered in your answer"""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """Initialize the QA agent with language model."""
        model_source = os.getenv("MODEL_SOURCE", "google")

        if model_source == "google":
            self.model = ChatGoogleGenerativeAI(
                model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-exp")
            )
        else:
            self.model = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                temperature=0.7,
            )

        # Create the agent with structured output
        self.graph = create_react_agent(
            self.model,
            tools=[],  # No tools needed for this example
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.FORMAT_INSTRUCTION, AnswerWithFollowups),
        )

    async def stream(
        self, query: str, context_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """Stream the agent's response.

        Args:
            query: The user's question
            context_id: The conversation context ID

        Yields:
            Dictionary containing task status and content
        """
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": context_id}}

        # Stream intermediate updates if needed
        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if isinstance(message, AIMessage):
                # Optional: yield progress updates
                yield {
                    "is_task_complete": False,
                    "content": "Thinking...",
                }

        # Get the final structured response
        yield self.get_agent_response(config)

    def get_agent_response(self, config) -> dict[str, Any]:
        """Extract the structured response from agent state.

        Args:
            config: The agent configuration

        Returns:
            Dictionary with the answer and follow-up data
        """
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get("structured_response")

        if structured_response and isinstance(structured_response, AnswerWithFollowups):
            # Return both the text answer and structured follow-up data
            return {
                "is_task_complete": True,
                "answer_text": structured_response.answer,
                "follow_up_data": {
                    "follow_up_questions": structured_response.follow_up_questions,
                    "confidence": structured_response.confidence,
                    "topics": structured_response.topics,
                },
            }

        # Fallback if structured response is not available
        return {
            "is_task_complete": False,
            "answer_text": "Unable to generate a response. Please try again.",
            "follow_up_data": {
                "follow_up_questions": [],
                "confidence": 0.0,
                "topics": [],
            },
        }
