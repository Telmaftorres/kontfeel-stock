"""
Lance ce script une seule fois après le déploiement pour créer la première clé API admin.
Usage : python seed_first_key.py
"""
import asyncio
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.core.security import generate_key
from app.models.api_key import ApiKey


async def main():
    raw, hashed = generate_key()
    async with AsyncSessionLocal() as db:
        key = ApiKey(name="Admin", key_hash=hashed, created_at=datetime.now(timezone.utc))
        db.add(key)
        await db.commit()
    print(f"\n✅ Clé API admin créée — note-la, elle ne sera plus affichée :\n\n  {raw}\n")


asyncio.run(main())
