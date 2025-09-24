import httpx
import json

async def run_test_case(test_case):
    try:
        method = test_case.method.upper()
        payload = json.loads(test_case.payload) if test_case.payload else None

        async with httpx.AsyncClient() as client:
            resp = await client.request(method, test_case.endpoint, json=payload, timeout=10)
            success = 200 <= resp.status_code < 300
            status = resp.status_code
    except Exception:
        success = False
        status = 0

    return {"test_case_id": test_case.id, "success": success, "status": status}
