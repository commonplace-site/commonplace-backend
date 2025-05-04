from fastapi import APIRouter, FastAPI, Request
import httpx
import os
import uuid
from datetime import datetime


router = APIRouter(tags=["Slack"])
# Optional: set up forwarding URL for Slack logs (e.g., Aalam AI or CP platform)
SLACK_FORWARD_URL = os.getenv("SLACK_FORWARD_URL", "https://aalam.smartadroit.com/api/slack-events")


@app.post("/api/slack/cp-sync")
async def slack_cp_sync(request: Request):
    """Capture Slack uploads/comments for Control Panel sync."""
    payload = await request.json()

    # ✅ Basic validation
    user = payload.get("user", "unknown_user")
    text = payload.get("text", "")
    files = payload.get("files", [])
    timestamp = payload.get("ts", datetime.utcnow().isoformat())

    if not text and not files:
        return {"status": "error", "message": "No content to sync."}

    sync_id = str(uuid.uuid4())  # For tracking/logging
    event_data = {
        "sync_id": sync_id,
        "user": user,
        "text": text,
        "files": files,
        "timestamp": timestamp,
        "source": "slack"
    }

    print(f"📥 Slack CP Sync Received (ID: {sync_id})")

    # 🔁 Optional: Forward to Aalam AI or internal CP system
    try:
        async with httpx.AsyncClient() as client:
            forward_response = await client.post(SLACK_FORWARD_URL, json=event_data)
            print("📡 Forwarded to Aalam AI:", forward_response.status_code)
    except Exception as e:
        print("❌ Forwarding failed:", str(e))

    # 🕒 Optional: Queue this for async processing (placeholder logic)
    # e.g., you can push to Redis, database, or RabbitMQ here
    # redis_conn.lpush("slack_sync_queue", json.dumps(event_data))

    return {
        "status": "queued",
        "message": "Slack message captured successfully.",
        "sync_id": sync_id
    }
