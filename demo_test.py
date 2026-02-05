import asyncio
import json
import httpx
from uuid import uuid4

async def test():
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            'http://localhost:9998',
            json={
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": str(uuid4()),
                        "role": "user",
                        "parts": [{"kind": "text", "text": "What is quantum computing?"}]
                    }
                },
                "id": 1
            }
        )
        result = response.json()
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        task = result['result']
        print(f"\n{'='*80}")
        print("QA AGENT MULTI-PART RESPONSE DEMO")
        print(f"{'='*80}\n")
        print(f"Task State: {task['state']}\n")
        
        for artifact in task.get('artifacts', []):
            for idx, part in enumerate(artifact['parts'], 1):
                kind = part['kind']
                print(f"\n{'#'*80}")
                print(f"# PART {idx}: {kind.upper()}")
                print(f"{'#'*80}\n")
                if kind == 'text':
                    print(part['text'][:500] + "...")
                elif kind == 'data':
                    print(json.dumps(part['data'], indent=2))
                print()

asyncio.run(test())
