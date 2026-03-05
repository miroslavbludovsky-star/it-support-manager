from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.settings import AppSettings
from app.schemas.settings import SettingResponse, SettingUpdateRequest

router = APIRouter()

DEFAULT_SETTINGS = {
    "llm_prompt": (
        "Jsi asistent projektového manažera v IT firmě Marbes. Píšeš profesionální emaily\n"
        "v češtině. Tvůj styl komunikace je inspirovaný Chris Vossem (Never Split the\n"
        "Difference) - používáš taktickou empatii, zrcadlení, otevřené kalibrované otázky\n"
        "a pozitivní formulace. Jsi diplomatický, empatický, ale asertivní.\n\n"
        "Pravidla:\n"
        "- Piš stručně a věcně, ale vřele a lidsky\n"
        "- Vždy používej oslovení a pozdrav\n"
        "- Nikdy neslibuj konkrétní termíny, pokud nemáš data\n"
        "- Pokud jde o technický problém, potvrzuj porozumění a nabízej další kroky\n"
        "- U interních mailů buď méně formální než u externích\n"
        '- Používej "Jak bych vám mohl nejlépe pomoci?" místo "Co potřebujete?"\n'
        '- Pojmenovávej emoce protistrany: "Zdá se, že vás to frustruje..."\n'
        '- Používej pozdrav "S pozdravem" nebo "S úctou" podle formality'
    ),
    "jira_sender": "mailer@marbes.cz",
    "sync_interval": "5",
}


@router.get("/settings", response_model=list[SettingResponse])
async def list_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppSettings))
    settings = result.scalars().all()

    # Return defaults for missing keys
    existing_keys = {s.key for s in settings}
    response = list(settings)
    for key, value in DEFAULT_SETTINGS.items():
        if key not in existing_keys:
            response.append(AppSettings(key=key, value=value))
    return response


@router.get("/settings/{key}", response_model=SettingResponse)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        default = DEFAULT_SETTINGS.get(key, "")
        return SettingResponse(key=key, value=default)
    return setting


@router.put("/settings/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    update: SettingUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = update.value
    else:
        setting = AppSettings(key=key, value=update.value)
        db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return setting
