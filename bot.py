from shadpy import Client
from shadpy.types import Updates
from lists import jokes, facts, motivations
from ai import ask_gpt
import random, json, os, datetime, jdatetime, math, re

DATA_FILE = "data.json"

# Create data file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "suggestions": []}, f, ensure_ascii=False, indent=2)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

bot = Client(name="shadpy")

@bot.on_message_updates()
async def handle_message(update: Updates):
    chat_id = update.object_guid
    user_text = (update.text or "").strip()

    # Register new user
    if chat_id not in data["users"]:
        data["users"].append(chat_id)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Static replies
    if user_text == "سلام":
        await update.reply("سلام عزیز دل! 🫶🌸")

    elif user_text == "جوک":
        await update.reply("😂 " + random.choice(jokes))

    elif user_text == "دانستنی":
        await update.reply("📚 " + random.choice(facts))

    elif user_text == "انگیزشی":
        await update.reply("🌟 " + random.choice(motivations))

    elif user_text == "ساعت":
        now = datetime.datetime.now().strftime("%H:%M:%S")
        await update.reply(f"🕰 ساعت الان: {now}")

    elif user_text == "تاریخ":
        today = jdatetime.date.today().strftime("%Y/%m/%d")
        await update.reply(f"📅 امروز: {today}")

    elif user_text == "زمان دقیق":
        now = datetime.datetime.now().strftime("%H:%M:%S")
        today = jdatetime.date.today().strftime("%Y/%m/%d")
        await update.reply(f"📆 امروز: {today}\n🕰 ساعت: {now}")

    elif user_text == "شانسی":
        await update.reply(f"🎲 عدد شانسی تو: {random.randint(1, 100)}")

    elif user_text == "تست هوش":
        await update.reply("🧠 اگر قطار ۱۲۰ و موتور ۸۰ بره، کدوم زودتر می‌رسه؟ 😉")

    elif user_text == "تعداد کاربرا":
        count = len(data["users"])
        await update.reply(f"👥 تعداد کاربران ثبت‌شده: {count} نفر")

    elif user_text.startswith("جمله انگیزشی جدید"):
        await update.reply("🚀 موفقیت از تلاش بی‌وقفه ساخته میشه، نه شانس!")

    elif user_text.startswith("معکوس "):
        text = user_text[7:].strip()
        if text:
            reversed_text = text[::-1]
            await update.reply(f"🔁 معکوس: {reversed_text}")
        else:
            await update.reply("متنی وارد نکردی که معکوس کنم! 😅")

    elif user_text.startswith("بگو "):
        text = user_text[4:].strip()
        if text:
            await update.reply(f"🗣 {text}")
        else:
            await update.reply("چی بگم؟ متن ننوشتی 😅")

    elif user_text == "کمک":
        help_text = (
            "📜 دستورهای بات:\n"
            "🔹 سلام | جوک | دانستنی | انگیزشی | جمله انگیزشی جدید\n"
            "🔹 ساعت | تاریخ | زمان دقیق\n"
            "🔹 شانسی | تست هوش | تعداد کاربرا\n"
            "🔹 بگو [متن] | معکوس [متن]\n"
            "🔹 محاسبه [عبارت]  → مثال: محاسبه 5*3+2\n"
            "🔹 تکرار [متن] *[تعداد] → مثال: تکرار سلام *3\n"
            "🔹 بات [سؤال] | پیشنهاد [متن]"
        )
        await update.reply(help_text)

    elif user_text == "مشخصات":
        chat_type = 'خصوصی' if update.chat_type == 'pv' else 'گروه'
        await update.reply(f"🆔 آیدی: {chat_id}\n💬 نوع چت: {chat_type}")

    # Math expression evaluator
    elif user_text.startswith("محاسبه "):
        expr = user_text[8:].strip()
        try:
            result = eval(expr, {"__builtins__": None}, vars(math))
            await update.reply(f"🧮 نتیجه: {result}")
        except Exception:
            await update.reply("❌ فرمول نامعتبر بود!")

    # Repeat text X times
    elif user_text.startswith("تکرار "):
        body = user_text[6:].strip()
        match = re.match(r"(.+)\s\*(\d+)$", body)
        if match:
            text, count = match.group(1).strip(), int(match.group(2))
            count = min(count, 10)
            await update.reply((text + "\n") * count)
        else:
            await update.reply("📌 فرمت درست نیست. مثال: تکرار سلام *3")

    # Store suggestion
    elif user_text.startswith("پیشنهاد "):
        suggestion = user_text[9:].strip()
        if suggestion:
            data.setdefault("suggestions", []).append({"from": chat_id, "text": suggestion})
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            await update.reply("💡 پیشنهادت ثبت شد! ممنونم ازت 🌟")
        else:
            await update.reply("بعد از «پیشنهاد» متن رو بنویس لطفاً 😊")

    # Ask ChatGPT
    elif user_text.startswith("بات "):
        prompt = user_text[4:].strip()
        if prompt:
            response = await ask_gpt(prompt)
            await update.reply(response)
        else:
            await update.reply("❗ لطفاً یک پیام بعد از 'بات' بنویس.")

bot.run()
