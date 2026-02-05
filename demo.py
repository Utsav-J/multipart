"""Demo script to test the QA agent and show multi-part responses."""

import asyncio
import json
from uuid import uuid4

import httpx


async def demo_qa_agent():
    """Demonstrate the multi-part response from QA agent."""
    agent_url = 'http://localhost:9998'
    
    print("\n" + "=" * 80)
    print(" " * 20 + "QA AGENT WITH MULTI-PART RESPONSES - DEMO")
    print("=" * 80 + "\n")
    
    # Test question
    question = "What is quantum computing?"
    print(f"📤 SENDING QUESTION: '{question}'")
    print("-" * 80 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Send message using JSON-RPC
        response = await client.post(
            agent_url,
            json={
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": str(uuid4()),
                        "role": "user",
                        "parts": [
                            {
                                "kind": "text",
                                "text": question
                            }
                        ]
                    }
                },
                "id": 1
            }
        )
        
        result = response.json()
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        task = result.get('result', {})
        
        print(f"✅ Task completed successfully!")
        print(f"   Task ID: {task.get('id')}")
        print(f"   State: {task.get('state')}")
        print("\n" + "=" * 80)
        
        # Process artifacts
        artifacts = task.get('artifacts', [])
        if not artifacts:
            print("⚠️  No artifacts in response")
            return
        
        for artifact_idx, artifact in enumerate(artifacts, 1):
            print(f"\n📦 ARTIFACT #{artifact_idx}")
            print("-" * 80)
            
            parts = artifact.get('parts', [])
            print(f"Number of parts: {len(parts)}\n")
            
            for part_idx, part in enumerate(parts, 1):
                part_kind = part.get('kind', 'unknown')
                
                if part_kind == 'text':
                    print(f"\n{'#' * 80}")
                    print(f"# PART {part_idx}: TEXT (Human-Readable Answer)")
                    print(f"{'#' * 80}\n")
                    
                    text_content = part.get('text', '')
                    print(text_content)
                    print()
                
                elif part_kind == 'data':
                    print(f"\n{'#' * 80}")
                    print(f"# PART {part_idx}: DATA (Structured Follow-ups & Metadata)")
                    print(f"{'#' * 80}\n")
                    
                    data_content = part.get('data', {})
                    
                    # Display follow-up questions
                    if 'follow_up_questions' in data_content:
                        print("🔮 FOLLOW-UP QUESTIONS:")
                        print("-" * 80)
                        for i, q in enumerate(data_content['follow_up_questions'], 1):
                            print(f"  {i}. {q}")
                        print()
                    
                    # Display confidence
                    if 'confidence' in data_content:
                        confidence = data_content['confidence'] * 100
                        print(f"📊 CONFIDENCE SCORE: {confidence:.1f}%")
                        print()
                    
                    # Display topics
                    if 'topics' in data_content:
                        print(f"🏷️  TOPICS: {', '.join(data_content['topics'])}")
                        print()
                    
                    # Display metadata if present
                    if 'response_metadata' in data_content:
                        print("📋 METADATA:")
                        for key, value in data_content['response_metadata'].items():
                            print(f"   {key}: {value}")
                        print()
                    
                    print("-" * 80)
                    print("RAW JSON DATA:")
                    print("-" * 80)
                    print(json.dumps(data_content, indent=2))
                    print()
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE - Multi-Part Response Pattern Demonstrated!")
        print("=" * 80)
        print("\n📝 KEY TAKEAWAY:")
        print("   The response contains 2 parts:")
        print("   • Part 1 (TextPart): Human-readable answer")
        print("   • Part 2 (DataPart): Structured data for UI/processing")
        print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    try:
        asyncio.run(demo_qa_agent())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
