import json
import asyncio
from functools import wraps

from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = 0
API_HASH = ""
SESSION = ""
GROUP_ID = 0
K_DEFENDER_ID = 0
CHAT_TOKEN = ""

_bot = None
_mt = None
_group_entity = None
_lock = asyncio.Lock()

kdefender_cmd = [ "/start", "/help", "/get_info", "/settings", "/menu" ]

class KDefenderNotReady(RuntimeError):
    pass


async def setup(bot=None, api_id=None, api_hash=None, session=None, group_id=None, chat_token=None, kdefender_id=None):
    """
    One-line setup:
        await kdefender_setup(bot)
    """

    missing = []

    if bot is None:
        missing.append("bot")
    if not api_id:
        missing.append("api_id")
    if not api_hash:
        missing.append("api_hash")
    if not session:
        missing.append("session")
    if not group_id:
        missing.append("group_id")
    if not chat_token:
        missing.append("chat_token")
    if not kdefender_id:
        missing.append("kdefender_id")

    if missing:
        raise KDefenderNotReady(
            "K-Defender wrapper not configured. Missing: " + ", ".join(missing)
        )

    global _bot, _mt, API_ID, API_HASH, SESSION, GROUP_ID, CHAT_TOKEN, K_DEFENDER_ID, _group_entity
    API_ID = int(api_id)
    API_HASH = str(api_hash)
    SESSION = str(session)
    GROUP_ID = int(group_id)
    CHAT_TOKEN = str(chat_token)
    K_DEFENDER_ID = int(kdefender_id)

    _bot = bot

    # Start Telethon; if it fails, ensure no half-open client remains
    if _mt is None:
        _mt = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
        await _mt.start()
        _group_entity = await _mt.get_input_entity(GROUP_ID)


async def close():
    """Call on shutdown."""
    global _mt
    if _mt and _mt.is_connected():
        await _mt.disconnect()
    _mt = None


async def _send_and_wait_verdict(text: str, timeout: int = 10) -> bool:
    """
    Sends:
        "<text>\n__TOKEN__:<CHAT_TOKEN>"
    and waits for K-Defender JSON verdict in the group.
    """
    if _bot is None or _mt is None:
        raise KDefenderNotReady("Call await setup(...) before using @kdefender_check().")
    
    async with _lock:
        verdict = False
        got_reply = asyncio.Event()

        async def handler(event):
            nonlocal verdict

            raw = (event.raw_text or "").strip()
            if not raw:
                return
            first_line = raw.splitlines()[0].strip()

            if not first_line.startswith("{"):
                return

            try:
                data = json.loads(first_line)
            except Exception:
                return

            if "result" not in data:
                return

            verdict = (data.get("result") == "ok")
            got_reply.set()

        event_filter = events.NewMessage(chats=_group_entity, from_users=K_DEFENDER_ID)
        _mt.add_event_handler(handler, event_filter)

        await _bot.send_message(GROUP_ID, f"{text}\n__TOKEN__:{CHAT_TOKEN}")

        try:
            await asyncio.wait_for(got_reply.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            verdict = False
        finally:
            try:
                _mt.remove_event_handler(handler, event_filter)
            except Exception:
                pass

        return verdict


def _extract_user_text(update) -> str | None:
    """
    Supports:
      - aiogram.types.Message: message.text or caption
      - aiogram.types.CallbackQuery: callback.data
    """
    # Message
    text = getattr(update, "text", None)
    if text:
        return text

    caption = getattr(update, "caption", None)
    if caption:
        return caption

    # CallbackQuery
    data = getattr(update, "data", None)
    if data:
        return data

    return None


def _blocked_reply_target(update):
    if hasattr(update, "answer") and not hasattr(update, "data"):
        return update
    
    msg = getattr(update, "message", None)
    if msg and hasattr(msg, "answer"):
        return msg

    return None


def kdefender_check():
    """
    Decorator:
        @kdefender_check()
        async def handler(message: Message): ...

    It will:
      - read user input text
      - ask K-Defender for verdict
      - if blocked: reply "Message blocked..." and stop
      - else: run your handler
    """
    def deco(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # find first "update-like" argument (Message/CallbackQuery/etc)
            update = None
            for a in args:
                if hasattr(a, "chat") or hasattr(a, "data") or hasattr(a, "from_user"):
                    update = a
                    break
            if update is None:
                update = next(iter(kwargs.values()), None)

            text = _extract_user_text(update) if update else None

            chat = getattr(update, "chat", None)
            chat_id = getattr(chat, "id", None)

            if chat_id == GROUP_ID:
                return
            
            for cmd in kdefender_cmd:
                if text and text.startswith(cmd):
                    text = ''.join(text.split(cmd, 1))
                    
            text = text.strip()

            if not text:
                return await func(*args, **kwargs)

            ok = await _send_and_wait_verdict(text)

            if not ok:
                target = _blocked_reply_target(update)
                if target:
                    await target.answer("Message blocked by 🛡️K-Defender🔐")
                return

            return await func(*args, **kwargs)
        return wrapper
    return deco
