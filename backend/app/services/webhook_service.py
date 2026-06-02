import httpx
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import Webhook, WebhookLog


async def dispatch(db: AsyncSession, event: str, payload: dict) -> None:
    """Envoie le payload à tous les webhooks actifs abonnés à cet event."""
    result = await db.execute(select(Webhook).where(Webhook.is_active == True))
    webhooks = result.scalars().all()

    for wh in webhooks:
        subscribed = [e.strip() for e in wh.events.split(",")]
        if event not in subscribed and "movement" not in subscribed:
            continue

        status_code = None
        error = None
        headers = {"Content-Type": "application/json", "X-Kstock-Event": event}
        if wh.secret:
            headers["X-Kstock-Secret"] = wh.secret

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(wh.url, json=payload, headers=headers)
                status_code = r.status_code
        except Exception as exc:
            error = str(exc)

        log = WebhookLog(
            webhook_id=wh.id,
            event=event,
            status_code=status_code,
            error=error,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log)

    await db.commit()
