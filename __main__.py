"""Main entry point for QA with Follow-ups Agent."""

import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from agent_executor import QAWithFollowupsAgentExecutor


if __name__ == '__main__':
    # Define the agent skill
    skill = AgentSkill(
        id='qa_with_followups',
        name='Question Answering with Follow-up Suggestions',
        description=(
            'Answers questions comprehensively and generates relevant '
            'follow-up questions to continue the conversation'
        ),
        tags=['qa', 'follow-ups', 'conversation'],
        examples=[
            'What is quantum computing?',
            'Explain how neural networks work',
            'What are the benefits of renewable energy?',
        ],
    )

    # Define the agent card
    agent_card = AgentCard(
        name='QA Agent with Follow-ups',
        description=(
            'An intelligent Q&A agent that provides detailed answers and '
            'suggests relevant follow-up questions. Returns responses in '
            'two parts: a text answer and structured follow-up data.'
        ),
        url='http://localhost:9998/',
        version='1.0.0',
        default_input_modes=['text', 'text/plain'],
        default_output_modes=['text', 'text/plain'],
        capabilities=AgentCapabilities(
            streaming=True,
            push_notifications=False,
        ),
        skills=[skill],
    )

    # Create the request handler
    request_handler = DefaultRequestHandler(
        agent_executor=QAWithFollowupsAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create the A2A server
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    # Run the server
    print('🚀 Starting QA with Follow-ups Agent on port 9998')
    print('📝 This agent returns multi-part responses:')
    print('   - Part 1 (TextPart): The answer')
    print('   - Part 2 (DataPart): Follow-up questions and metadata')
    print()
    uvicorn.run(server.build(), host='0.0.0.0', port=9998)  # noqa: S104
