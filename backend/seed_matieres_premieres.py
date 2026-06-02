"""
Peuple le catalogue des matières premières.
Usage : docker compose exec api python seed_matieres_premieres.py
"""
import asyncio

from app.core.database import AsyncSessionLocal
from app.models.matiere_premiere import MatierePremiere

CATALOGUE = [
    ("Akylux 3mm",                    "1200x1600",  "feuille"),
    ("BC 30 2 bruns (BCTT74A)",       "1700x2200",  "feuille"),
    ("BC 30 2 bruns (BCTT74A)",       "1700x2100",  "feuille"),
    ("C (C5TT52A)",                   "1700x2100",  "feuille"),
    ("Carte 300 gr",                  "720x1020",   "feuille"),
    ("Carte 350 gr couche 1 face",    "800x1200",   "feuille"),
    ("Carte 400 gr couché 2 blanc",   "800x1200",   "feuille"),
    ("Compact 10/19",                 "1200x1600",  "feuille"),
    ("DISPA",                         "1524x1016",  "feuille"),
    ("E 1C/1B (11S1W)",               "1700x2100",  "feuille"),
    ("EE 1 kraft brun / 1 brun",      "1700x2100",  "feuille"),
    ("EE 1C/1B (20S1G1W)",            "2000x2500",  "feuille"),
    ("EE 1C/1B (20S1G1W)",            "1670x2400",  "feuille"),
    ("EE 1C/1B (20S1G1W)",            "1700x2100",  "feuille"),
    ("EE 2C (20W1G1W)",               "1700x2100",  "feuille"),
    ("PET transparent 0,5mm",         "2050x1250",  "feuille"),
    ("PRIPLAK blanc 1200 microns",    "800x1200",   "feuille"),
    ("PVC 1 mm",                      "2440x1220",  "feuille"),
    ("PVC 3 mm",                      "1525x2050",  "feuille"),
    ("PVC 300 microns",               "1000x1400",  "feuille"),
    ("PVC 5 mm",                      "2050x1525",  "feuille"),
    ("PVC 500 microns",               "1000x1400",  "feuille"),
    ("PVC 500 microns",               "850x1250",   "feuille"),
    ("PVC 700 micron",                "1000x1400",  "feuille"),
    ("PVC blanc 3 mm",                "2440x1220",  "feuille"),
    ("Vinyl adhesif blanc",           "700x1000",   "feuille"),
    ("Vinyl adhesif transparent",     "1000x700",   "feuille"),
]


async def main():
    async with AsyncSessionLocal() as db:
        for nom, format_, unite in CATALOGUE:
            db.add(MatierePremiere(nom=nom, format=format_, unite=unite))
        await db.commit()
    print(f"✅ {len(CATALOGUE)} matières premières importées.")


asyncio.run(main())
