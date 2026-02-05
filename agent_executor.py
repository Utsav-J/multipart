"""Agent Executor for QA with Follow-ups Agent.

This executor demonstrates how to send multi-part responses:
1. TextPart: containing the answer
2. DataPart: containing structured follow-up questions and metadata
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from agent import QAWithFollowupsAgent


class QAWithFollowupsAgentExecutor(AgentExecutor):
    """Agent Executor that sends multi-part responses (text + data)."""

    def __init__(self):
        """Initialize the agent executor."""
        self.agent = QAWithFollowupsAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the agent and send multi-part response.

        This method demonstrates the key pattern:
        1. Get answer and follow-up data from the agent
        2. Create TextPart for the answer
        3. Create DataPart for the structured follow-ups
        4. Send both parts together using add_artifact

        Args:
            context: The request context
            event_queue: The event queue for sending responses
        """
        query = context.get_user_input()
        task = context.current_task

        # Create task if it doesn't exist
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # Stream the agent's response
        async for item in self.agent.stream(query, task.context_id):
            is_task_complete = item['is_task_complete']

            # Send progress updates
            if not is_task_complete:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(
                        item.get('content', 'Processing...'),
                        task.context_id,
                        task.id,
                    ),
                )
                continue

            # ===== KEY PATTERN: Multi-Part Response =====
            # Extract the answer text and follow-up data
            answer_text = item.get('answer_text', '')
            follow_up_data = item.get('follow_up_data', {})

            # Create the multi-part response
            parts = [
                # Part 1: Text answer for human consumption
                Part(root=TextPart(text=answer_text)),
                
                # Part 2: Structured data for follow-ups and metadata
                Part(root=DataPart(data=follow_up_data)),
            ]

            # Send the multi-part artifact
            await updater.add_artifact(
                parts,
                name='qa_response',  # Optional: name the artifact
            )

            # Mark task as complete
            await updater.complete()
            break

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> Task | None:
        """Cancel the current task.

        Args:
            context: The request context
            event_queue: The event queue

        Raises:
            ServerError: Cancel operation is not supported
        """
        raise ServerError(error=UnsupportedOperationError())
