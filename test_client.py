"""Test client for QA with Follow-ups Agent.

This script demonstrates how to call the agent and process multi-part responses.
"""

import asyncio
import json

from a2a.types import Message, Part, TextPart
from a2a.utils import a2a_grpc_client


async def test_qa_agent():
    """Test the QA agent with a sample question."""
    agent_url = 'http://localhost:9998/a2a/v1'
    
    # Create a test message
    test_question = 'What is quantum computing and why is it important?'
    
    print(f'📤 Sending question: {test_question}')
    print('=' * 70)
    
    # Create the message
    message = Message(
        role='user',
        parts=[Part(root=TextPart(text=test_question))],
    )
    
    # Send the message to the agent
    async with a2a_grpc_client(agent_url) as client:
        # Send message and get task
        task = await client.message_send(new_message=message)
        
        print(f'✅ Task created: {task.id}')
        print()
        
        # The response will have artifacts with multiple parts
        if task.artifacts:
            for idx, artifact in enumerate(task.artifacts):
                print(f'📦 Artifact {idx + 1}:')
                
                for part_idx, part in enumerate(artifact.parts):
                    if isinstance(part.root, TextPart):
                        print(f'\n📝 Part {part_idx + 1} - TextPart (Answer):')
                        print('-' * 70)
                        print(part.root.text)
                        print('-' * 70)
                    
                    elif hasattr(part.root, 'data'):
                        print(f'\n📊 Part {part_idx + 1} - DataPart (Follow-ups):')
                        print('-' * 70)
                        data = part.root.data
                        
                        # Display follow-up questions
                        if 'follow_up_questions' in data:
                            print('\n🔮 Suggested Follow-up Questions:')
                            for i, question in enumerate(data['follow_up_questions'], 1):
                                print(f'  {i}. {question}')
                        
                        # Display confidence
                        if 'confidence' in data:
                            confidence_pct = data['confidence'] * 100
                            print(f'\n📈 Confidence: {confidence_pct:.1f}%')
                        
                        # Display topics
                        if 'topics' in data:
                            print(f'\n🏷️  Topics: {", ".join(data["topics"])}')
                        
                        print()
                        print('Raw JSON:')
                        print(json.dumps(data, indent=2))
                        print('-' * 70)
        else:
            print('⚠️  No artifacts in response')
        
        print()
        print('✅ Test completed!')


if __name__ == '__main__':
    asyncio.run(test_qa_agent())
