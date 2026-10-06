import httpx
import os
import urllib.parse

API_BASE_URL = os.getenv("FAST_CREAT_BASE_URL", "https://api.fast-creat.ir/gpt/chat")
API_KEY = os.getenv("FAST_CREAT_API_KEY", "1114526010:fH5ay4sG0kSU9hc@SenatorApiBot")


async def ask_gpt(prompt: str) -> str:
    if not prompt or not prompt.strip():
        return "❗ متن سوال خالی است."

    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{API_BASE_URL}?apikey={API_KEY}&text={encoded_prompt}"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("ok") and "result" in data and isinstance(data["result"], dict):
                text = data["result"].get("text")
                if text:
                    return text
            return "❌ پاسخ نامعتبر از سمت سرور دریافت شد."
    except Exception as exc:  # pragma: no cover - network error handling
        return f"❌ خطا در ارتباط با API:\n{exc}"
