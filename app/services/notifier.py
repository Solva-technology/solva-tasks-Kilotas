import httpx
import logging


log = logging.getLogger(__name__)
TELEGRAM_API = "https://api.telegram.org"


import httpx
import logging
from app.core.config import settings

log = logging.getLogger(__name__)
TELEGRAM_API = "https://api.telegram.org"


async def send_tg_message(chat_id: str, text: str) -> bool:
    if not getattr(settings, "BOT_TOKEN", None):
        log.error({"action": "telegram_skip", "reason": "no_bot_token"})
        return False

    url = f"{TELEGRAM_API}/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)

        ok = False
        body = resp.text
        try:
            data = resp.json()
            ok = resp.status_code == 200 and data.get("ok") is True
        except Exception:
            pass

        log.info(
            {
                "action": "telegram_send",
                "chat_id": chat_id,
                "status_code": resp.status_code,
                "ok": ok,
                "response": body[:600],
            }
        )
        if not ok:
            log.error(
                {
                    "action": "telegram_fail",
                    "chat_id": chat_id,
                    "status_code": resp.status_code,
                    "response": body[:600],
                }
            )
        return ok

    except Exception as e:
        log.exception(
            {"action": "telegram_exception", "chat_id": chat_id, "error": str(e)}
        )
        return False
