from fastapi import APIRouter, FastAPI, Request, Header, HTTPException
import hmac
import hashlib
import json

import httpx

router = APIRouter(tags=["Github-Web-Hook"])
GITHUB_SECRET = b"supersecret123"  # Same as in GitHub webhook setup

# Signature verification
def verify_signature(payload_body, signature):
    mac = hmac.new(GITHUB_SECRET, msg=payload_body, digestmod=hashlib.sha256)
    expected = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

# ✅ Forward payload to Aalam AI
async def forward_to_aalam(data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://aalam.smartadroit.com/api/github-events",
            json=data
        )
        print(f"✔️ Forwarded to Aalam: {response.status_code}")
        return response.status_code

# ✅ Webhook endpoint
@router.post("/api/github/events")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None)
):
    body = await request.body()

    # 🛡️ Validate GitHub signature
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body)
    print(f"🔔 GitHub Event Received: {x_github_event}")
    
    # 🔁 Forwarding to Aalam AI
    status = await forward_to_aalam(payload)

    return {"message": "Webhook received and forwarded", "forward_status": status}
