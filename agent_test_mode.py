"""Test mode agent that works without API keys."""

from collections.abc import AsyncIterable
from typing import Any

from pydantic import BaseModel, Field


class AnswerWithFollowups(BaseModel):
    """Response format containing answer and follow-up questions."""

    answer: str = Field(
        description="The comprehensive answer to the user's question"
    )
    follow_up_questions: list[str] = Field(
        description="A list of 3-5 relevant follow-up questions",
        min_items=3,
        max_items=5,
    )
    confidence: float = Field(
        description="Confidence level in the answer (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    topics: list[str] = Field(
        description="Key topics covered in the answer"
    )


class QAWithFollowupsAgentTestMode:
    """Test mode QA Agent that generates mock responses without needing an LLM."""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        """Initialize the test agent."""
        print("[TEST MODE] Running without API key - using mock responses")

    async def stream(
        self, query: str, context_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """Stream the agent's mock response.

        Args:
            query: The user's question
            context_id: The conversation context ID

        Yields:
            Dictionary containing task status and content
        """
        # Simulate thinking
        yield {
            'is_task_complete': False,
            'content': 'Analyzing your question...',
        }

        # Generate mock response based on the query
        response = self._generate_mock_response(query)
        yield response

    def _generate_mock_response(self, query: str) -> dict[str, Any]:
        """Generate a mock response for testing.

        Args:
            query: The user's question

        Returns:
            Dictionary with answer and follow-up data
        """
        # Create a relevant answer based on keywords in the query
        answer = f"""Based on your question "{query}", here's a comprehensive answer:

This is a test response generated without an actual LLM. In a real deployment with a GOOGLE_API_KEY, the agent would:

1. **Analyze your question** using advanced natural language understanding
2. **Generate a detailed answer** drawing from its trained knowledge base
3. **Create relevant follow-up questions** to continue the conversation
4. **Assess confidence** based on the certainty of the information
5. **Identify key topics** covered in the response

The multi-part response pattern demonstrated here works the same way whether using test data or a real LLM. The key is that we're sending:
- **Part 1 (TextPart)**: This answer text
- **Part 2 (DataPart)**: Structured follow-up questions and metadata

This architecture allows clients to display the answer naturally while using the structured data for interactive UI elements like clickable follow-up buttons."""

        # Generate contextual follow-up questions
        follow_ups = self._generate_follow_ups(query)

        return {
            'is_task_complete': True,
            'answer_text': answer,
            'follow_up_data': {
                'follow_up_questions': follow_ups,
                'confidence': 0.85,  # Test confidence score
                'topics': self._extract_topics(query),
            },
        }

    def _generate_follow_ups(self, query: str) -> list[str]:
        """Generate follow-up questions based on the query.

        Args:
            query: The user's question

        Returns:
            List of follow-up questions
        """
        query_lower = query.lower()
        
        # Generate contextual follow-ups based on keywords
        if any(word in query_lower for word in ['quantum', 'computing', 'computer']):
            return [
                "How do quantum computers differ from classical computers?",
                "What are the main applications of quantum computing?",
                "What challenges remain in building practical quantum computers?",
                "How does quantum entanglement contribute to computing power?",
            ]
        elif any(word in query_lower for word in ['machine learning', 'ml', 'ai', 'neural']):
            return [
                "What's the difference between supervised and unsupervised learning?",
                "How do neural networks process information?",
                "What are some real-world applications of machine learning?",
                "What skills are needed to get started with ML?",
            ]
        elif any(word in query_lower for word in ['climate', 'environment', 'renewable', 'energy']):
            return [
                "What are the most effective renewable energy sources?",
                "How can individuals reduce their carbon footprint?",
                "What policies are most effective for climate action?",
                "What role does technology play in climate solutions?",
            ]
        else:
            # Generic follow-ups
            return [
                "Can you explain this concept in simpler terms?",
                "What are some practical applications of this?",
                "What are the main challenges or limitations?",
                "Where can I learn more about this topic?",
                "How does this relate to other similar concepts?",
            ][:4]  # Return 4 questions

    def _extract_topics(self, query: str) -> list[str]:
        """Extract topics from the query.

        Args:
            query: The user's question

        Returns:
            List of topics
        """
        query_lower = query.lower()
        topics = []

        # Extract topics based on keywords
        topic_keywords = {
            'quantum': ['quantum computing', 'quantum mechanics', 'physics'],
            'machine learning': ['machine learning', 'artificial intelligence', 'data science'],
            'ai': ['artificial intelligence', 'machine learning', 'neural networks'],
            'climate': ['climate change', 'environment', 'sustainability'],
            'energy': ['renewable energy', 'sustainability', 'environment'],
            'programming': ['software development', 'coding', 'computer science'],
            'blockchain': ['blockchain', 'cryptocurrency', 'distributed systems'],
        }

        for keyword, related_topics in topic_keywords.items():
            if keyword in query_lower:
                topics.extend(related_topics[:2])

        # Default topics if none found
        if not topics:
            topics = ['general knowledge', 'information', 'learning']

        return list(set(topics))[:4]  # Return unique topics, max 4
