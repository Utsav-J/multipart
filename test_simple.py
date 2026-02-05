"""Simple test script to test the QA agent with multi-part responses."""

import asyncio
import json
import httpx


async def test_agent():
    """Test the QA agent."""
    agent_url = 'http://localhost:9998'
    
    print("=" * 70)
    print("Testing QA Agent with Multi-Part Responses")
    print("=" * 70)
    print()
    
    # Test 1: Get agent card
    print("[1] Getting agent card...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                agent_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "agent/card",
                    "id": 1
                },
                timeout=10.0
            )
            card_data = response.json()
            print(f"   Agent Name: {card_data.get('result', {}).get('name')}")
            print(f"   Version: {card_data.get('result', {}).get('version')}")
            print(f"   Description: {card_data.get('result', {}).get('description', '')[:80]}...")
            print()
    except Exception as e:
        print(f"   Error: {e}")
        print()
    
    # Test 2: Send a question and get multi-part response
    print("[2] Sending question: 'What is quantum computing?'")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                agent_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "messageId": "msg-001",
                            "role": "user",
                            "parts": [
                                {
                                    "kind": "text",
                                    "text": "What is quantum computing?"
                                }
                            ]
                        }
                    },
                    "id": 2
                },
                timeout=30.0
            )
            result = response.json()
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
                return
            
            task = result.get('result', {})
            print(f"   Task ID: {task.get('id')}")
            print(f"   Task State: {task.get('state')}")
            print()
            
            # Check for artifacts with multiple parts
            artifacts = task.get('artifacts', [])
            if artifacts:
                print(f"   Found {len(artifacts)} artifact(s)")
                print()
                
                for idx, artifact in enumerate(artifacts):
                    print(f"   === Artifact {idx + 1} ===")
                    parts = artifact.get('parts', [])
                    print(f"   Number of parts: {len(parts)}")
                    print()
                    
                    for part_idx, part in enumerate(parts):
                        part_kind = part.get('kind', 'unknown')
                        print(f"   --- Part {part_idx + 1}: {part_kind.upper()} ---")
                        
                        if part_kind == 'text':
                            text_content = part.get('text', '')
                            print(f"   {text_content[:200]}...")
                            print()
                        
                        elif part_kind == 'data':
                            data_content = part.get('data', {})
                            print(f"   Data keys: {list(data_content.keys())}")
                            
                            # Display follow-up questions
                            if 'follow_up_questions' in data_content:
                                print()
                                print("   Follow-up Questions:")
                                for i, question in enumerate(data_content['follow_up_questions'], 1):
                                    print(f"      {i}. {question}")
                            
                            # Display confidence
                            if 'confidence' in data_content:
                                confidence = data_content['confidence'] * 100
                                print(f"\n   Confidence: {confidence:.1f}%")
                            
                            # Display topics
                            if 'topics' in data_content:
                                print(f"   Topics: {', '.join(data_content['topics'])}")
                            
                            print()
                            print("   Full data:")
                            print("   " + json.dumps(data_content, indent=6))
                        
                        print()
            else:
                print("   No artifacts in response")
            
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_agent())
