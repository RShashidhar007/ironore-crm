"""
Thin wrapper around the local Ollama HTTP API.

Design rule (per system prompt): Ollama is used ONLY to phrase a
customer-friendly sentence around data the backend has already
verified from SQL Server. It is never asked to supply facts on its
own, and if it is unreachable the backend falls back to a clean
templated response built directly from the verified data — the bot
must keep working either way.
"""
import httpx

from .config import settings

SYSTEM_PROMPT = """You are a professional CRM assistant for a company that sells Iron Ore \
and Iron Pellet products. You will be given a block of VERIFIED_DATA that was retrieved \
directly from the company's database. Using ONLY that data, write a short, clear, \
customer-friendly reply.

Rules:
- Never invent numbers, product names, IDs, specifications, or customer details that are not \
present in VERIFIED_DATA.
- If VERIFIED_DATA says information is unavailable, tell the customer plainly that it \
could not be found — do not guess or fill gaps.
- Do not mention SQL, databases, tables, or internal system details.
- Keep the tone concise, polite, and professional.
- Do NOT create or show product specification tables unless explicitly requested in the customer message.
- Be conversational and helpful - focus on answering the customer's specific question or request.
"""


def is_available() -> bool:
    if not settings.OLLAMA_ENABLED:
        return False
    try:
        with httpx.Client(timeout=3) as client:
            r = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


def generate_reply(customer_message: str, verified_data: str) -> str | None:
    """
    Returns a generated reply string, or None if Ollama could not be
    reached / errored, so the caller can fall back to a template.
    """
    if not settings.OLLAMA_ENABLED:
        return None

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"CUSTOMER MESSAGE:\n{customer_message}\n\n"
        f"VERIFIED_DATA:\n{verified_data}\n\n"
        f"Write the reply now."
    )

    try:
        with httpx.Client(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = (data.get("response") or "").strip()
            return text or None
    except Exception:
        # Ollama down, model not pulled, timeout, etc. — fail soft.
        return None
