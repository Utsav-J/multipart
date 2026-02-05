"""Test the QA agent using A2A SDK client."""

import asyncio
import json
from uuid import uuid4

from a2a.client import A2AClient
from a2a.types import Message, TextPart


async def test_qa_agent():
    """Test the QA agent with multi-part responses."""
    agent_url = 'http://localhost:9998'
    
    print("=" * 70)
    print("Testing QA Agent with Multi-Part Responses")
    print("=" * 70)
    print()
    
    async with A2AClient(agent_url) as client:
        # Test 1: Get agent card
        print("[1] Getting agent card...")
        try:
            card = await client.get_card()
            print(f"   Agent Name: {card.name}")
            print(f"   Version: {card.version}")
            print(f"   Description: {card.description[:100]}...")
            print()
        except Exception as e:
            print(f"   Error: {e}")
            print()
        
        # Test 2: Send a message and get response
        print("[2] Sending question: 'What is quantum computing?'")
        print()
        
        message = Message(
            role='user',
            parts=[TextPart(text='What is quantum computing?')],
            message_id=str(uuid4()),
        )
        
        try:
            result = await client.send_message(message)
            
            print(f"   Task ID: {result.id}")
            print(f"   Task State: {result.state}")
            print(f"   Context ID: {result.context_id}")
            print()
            
            # Check artifacts
            if result.artifacts:
                print(f"   ✓ Found {len(result.artifacts)} artifact(s)")
                print()
                
                for idx, artifact in enumerate(result.artifacts):
                    print(f"   === Artifact {idx + 1} ===")
                    print(f"   Parts: {len(artifact.parts)}")
                    print()
                    
                    for part_idx, part in enumerate(artifact.parts):
                        print(f"   --- Part {part_idx + 1}: {part.root.kind.upper()} ---")
                        
                        if part.root.kind == 'text':
                            text_content = part.root.text
                            preview = text_content[:300] + "..." if len(text_content) > 300 else text_content
                            print(f"{preview}")
                            print()
                        
                        elif part.root.kind == 'data':
                            data_content = part.root.data
                            print(f"   Data keys: {list(data_content.keys())}")
                            print()
                            
                            # Display follow-up questions
                            if 'follow_up_questions' in data_content:
                                print("   📋 Follow-up Questions:")
                                for i, question in enumerate(data_content['follow_up_questions'], 1):
                                    print(f"      {i}. {question}")
                                print()
                            
                            # Display confidence
                            if 'confidence' in data_content:
                                confidence = data_content['confidence'] * 100
                                print(f"   📊 Confidence: {confidence:.1f}%")
                                print()
                            
                            # Display topics
                            if 'topics' in data_content:
                                print(f"   🏷️  Topics: {', '.join(data_content['topics'])}")
                                print()
                            
                            print("   Full JSON data:")
                            print(json.dumps(data_content, indent=6))
                            print()
                    
                    print()
            else:
                print("   ⚠️  No artifacts in response")
                print()
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_qa_agent())
