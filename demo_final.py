import asyncio, json, httpx
from uuid import uuid4

async def demo():
    print("\n" + "="*90)
    print(" "*25 + "🎯 MULTI-PART RESPONSE DEMO")
    print("="*90 + "\n")
    print("📤 Sending: 'What is quantum computing?'\n")
    
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post('http://localhost:9998', json={
            "jsonrpc": "2.0", "method": "message/send", "id": 1,
            "params": {"message": {
                "messageId": str(uuid4()), "role": "user",
                "parts": [{"kind": "text", "text": "What is quantum computing?"}]
            }}
        })
        result = r.json()
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        task = result.get('result', {})
        print(f"✅ Response received! Task: {task.get('id', 'N/A')[:8]}...\n")
        print("="*90 + "\n")
        
        for artifact in task.get('artifacts', []):
            parts = artifact.get('parts', [])
            print(f"📦 Artifact with {len(parts)} parts:\n")
            
            for idx, part in enumerate(parts, 1):
                kind = part.get('kind', 'unknown')
                print(f"{'▼'*90}")
                print(f"  PART {idx}: {kind.upper()} {'(Human-Readable Answer)' if kind=='text' else '(Structured Data)'}")
                print(f"{'▼'*90}\n")
                
                if kind == 'text':
                    text = part.get('text', '')
                    lines = text.split('\n')
                    for line in lines[:15]:  # Show first 15 lines
                        print(f"  {line}")
                    if len(lines) > 15:
                        print(f"\n  ... ({len(lines)-15} more lines)")
                    print()
                    
                elif kind == 'data':
                    data = part.get('data', {})
                    
                    if 'follow_up_questions' in data:
                        print("  🔮 FOLLOW-UP QUESTIONS:")
                        for i, q in enumerate(data['follow_up_questions'], 1):
                            print(f"     {i}. {q}")
                        print()
                    
                    if 'confidence' in data:
                        conf = data['confidence'] * 100
                        print(f"  📊 Confidence: {conf:.1f}%\n")
                    
                    if 'topics' in data:
                        print(f"  🏷️  Topics: {', '.join(data['topics'])}\n")
                    
                    print("  📋 Full JSON:")
                    print("  " + "-"*86)
                    for line in json.dumps(data, indent=4).split('\n'):
                        print(f"  {line}")
                    print()
        
        print("\n" + "="*90)
        print("✅ DEMO COMPLETE!")
        print("="*90)
        print("\n💡 Key Points:")
        print("   • Part 1 (TextPart): Main answer - display to users")
        print("   • Part 2 (DataPart): Structured data - use for buttons/UI/processing")
        print("   • Both parts sent together in ONE artifact\n")

asyncio.run(demo())
