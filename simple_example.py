"""Simple example showing multi-part response pattern WITHOUT LangGraph.

This minimal example demonstrates the core pattern of sending multi-part
responses in an A2A agent without the complexity of LangGraph integration.
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Part, TextPart
from a2a.utils import new_task


class SimpleQAAgent:
    """Simple Q&A agent that generates answers and follow-ups."""

    def generate_response(self, question: str) -> tuple[str, dict]:
        """Generate answer and follow-up questions.

        In a real implementation, this would call your LLM with a system prompt.
        For this example, we're simulating the response.

        Args:
            question: The user's question

        Returns:
            Tuple of (answer_text, follow_up_data)
        """
        # Simulate LLM response with system prompt instructions
        answer_text = f"""Based on your question about "{question}", here's a comprehensive answer:

Quantum computing is a revolutionary technology that leverages quantum mechanical 
phenomena to process information. Unlike classical computers that use bits (0 or 1), 
quantum computers use quantum bits or "qubits" that can exist in multiple states 
simultaneously through superposition.

This enables quantum computers to solve certain problems exponentially faster than 
classical computers, particularly in areas like cryptography, drug discovery, and 
optimization problems."""

        # Follow-up data structured as JSON
        follow_up_data = {
            'follow_up_questions': [
                'How do qubits differ from classical bits in terms of information storage?',
                'What are the main challenges in building practical quantum computers?',
                'Which industries are most likely to benefit from quantum computing first?',
                'How does quantum entanglement contribute to quantum computing power?',
            ],
            'confidence': 0.92,
            'topics': ['quantum computing', 'qubits', 'superposition', 'technology'],
            'response_metadata': {
                'word_count': len(answer_text.split()),
                'question_type': 'explanatory',
            },
        }

        return answer_text, follow_up_data


class SimpleQAAgentExecutor(AgentExecutor):
    """Agent Executor demonstrating multi-part response pattern."""

    def __init__(self):
        """Initialize the agent."""
        self.agent = SimpleQAAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute and send multi-part response.

        This is the KEY METHOD that shows the multi-part response pattern.
        """
        # 1. Get user input
        user_question = context.get_user_input()

        # 2. Get or create task
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # 3. Create task updater
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # 4. Generate response from your agent
        # (In real scenario: call LLM with system prompt)
        answer_text, follow_up_data = self.agent.generate_response(user_question)

        # ============================================================
        # 5. CREATE MULTI-PART RESPONSE - THIS IS THE KEY PATTERN
        # ============================================================
        parts = [
            # Part 1: TextPart containing the answer
            # This is what users will see as the main response
            Part(root=TextPart(text=answer_text)),
            
            # Part 2: DataPart containing structured follow-up questions
            # This can be parsed by clients for interactive UI elements
            Part(root=DataPart(data=follow_up_data)),
        ]

        # 6. Send the multi-part artifact
        await updater.add_artifact(
            parts,
            name='qa_response',  # Optional name for the artifact
        )

        # 7. Mark task as complete
        await updater.complete()

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Cancel not supported in this simple example."""
        raise NotImplementedError('Cancel not supported')


# ============================================================
# ALTERNATIVE PATTERNS
# ============================================================

class AlternativePatterns:
    """Examples of other multi-part response patterns."""

    @staticmethod
    async def example_three_parts(updater: TaskUpdater):
        """Send THREE parts: text + metadata + follow-ups."""
        parts = [
            Part(root=TextPart(text='Main answer here...')),
            Part(root=DataPart(data={
                'confidence': 0.95,
                'sources': ['source1', 'source2'],
            })),
            Part(root=DataPart(data={
                'follow_up_questions': ['Q1?', 'Q2?', 'Q3?'],
            })),
        ]
        await updater.add_artifact(parts)

    @staticmethod
    async def example_with_summary(updater: TaskUpdater):
        """Send summary text + detailed analysis data."""
        parts = [
            Part(root=TextPart(text='Summary: The analysis shows...')),
            Part(root=DataPart(data={
                'detailed_analysis': {
                    'metrics': {'accuracy': 0.95, 'precision': 0.92},
                    'insights': ['Insight 1', 'Insight 2'],
                    'recommendations': ['Do X', 'Consider Y'],
                },
            })),
        ]
        await updater.add_artifact(parts, name='analysis_result')

    @staticmethod
    async def example_conversational(updater: TaskUpdater):
        """Send response + conversation context."""
        parts = [
            Part(root=TextPart(text='Here is your answer...')),
            Part(root=DataPart(data={
                'conversation_state': {
                    'topic': 'quantum computing',
                    'user_expertise': 'beginner',
                    'suggested_next_topics': ['Topic A', 'Topic B'],
                },
            })),
        ]
        await updater.add_artifact(parts)


# ============================================================
# KEY TAKEAWAYS
# ============================================================
"""
1. Multi-part responses combine TextPart and DataPart in a single artifact

2. Basic pattern:
   parts = [
       Part(root=TextPart(text="answer")),
       Part(root=DataPart(data={...}))
   ]
   await updater.add_artifact(parts)

3. TextPart: For human-readable content
   - Main answer
   - Explanations
   - Summaries

4. DataPart: For structured, machine-readable content
   - Follow-up questions
   - Confidence scores
   - Metadata
   - Conversation state
   - Citations

5. Benefits:
   - Better UX: Show text naturally + use data programmatically
   - Enable rich UI: Render follow-ups as buttons/links
   - Preserve structure: No need to parse text for data
   - Multiple data types: Send as many parts as needed
"""
