# app/utils/webhook.py

import httpx
import logging

logger = logging.getLogger(__name__)

async def send_webhook(event_type: str, data: dict, url: str):
    """Sends a payload to a webhook URL asynchronously."""
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "event": event_type,
                "data": data
            }
            response = await client.post(url, json=payload, timeout=5.0)
            if response.status_code >= 400:
                logger.warning(f"Webhook {event_type} failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending webhook {event_type}: {str(e)}")
