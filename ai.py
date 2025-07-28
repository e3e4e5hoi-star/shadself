import httpx
import urllib.parse

async def ask_gpt(prompt: str) -> str:
    base_url = "https://api.fast-creat.ir/gpt/chat"
    apikey = "1114526010:fH5ay4sG0kSU9hc@SenatorApiBot"
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{base_url}?apikey={apikey}&text={encoded_prompt}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if data["ok"] and "result" in data and "text" in data["result"]:
                return data["result"]["text"]
            else:
                return "❌ پاسخ نامعتبر از سمت سرور دریافت شد."
    except Exception as e:
        return f"❌ خطا در ارتباط با API:\n{str(e)}"
