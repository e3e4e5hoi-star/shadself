import json
import math
import os
import random
import re
from datetime import datetime

try:
    import jdatetime  # type: ignore
except Exception:  # pragma: no cover
    jdatetime = None

try:
    from shadpy import Client
    from shadpy.types import Updates
except Exception:  # pragma: no cover
    Client = None
    Updates = object

from ai import ask_gpt
from lists import facts, jokes, motivations

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
BOT_NAME = os.getenv("BOT_NAME", "آقای X")

CHARACTERS = [
    {"name": "گرگعلی", "emoji": "🐺", "hp": 120, "attack": 22, "defense": 8},
    {"name": "محرم برموده", "emoji": "🛡️", "hp": 110, "attack": 19, "defense": 12},
    {"name": "مظفر شکری", "emoji": "⚔️", "hp": 130, "attack": 18, "defense": 16},
    {"name": "آرمین پلاس", "emoji": "💥", "hp": 140, "attack": 20, "defense": 11},
    {"name": "قائم سیربا", "emoji": "🦅", "hp": 115, "attack": 24, "defense": 9},
    {"name": "سینا غفاری", "emoji": "🐲", "hp": 135, "attack": 21, "defense": 10},
    {"name": "یاسر پسرک", "emoji": "🔥", "hp": 125, "attack": 25, "defense": 7},
    {"name": "کمال آریا", "emoji": "🧠", "hp": 100, "attack": 28, "defense": 6},
    {"name": "عباس سوار", "emoji": "🏹", "hp": 118, "attack": 23, "defense": 8},
    {"name": "امیر سلحشور", "emoji": "👑", "hp": 150, "attack": 17, "defense": 18},
]

DEFAULT_DATA = {"users": [], "suggestions": [], "profiles": {}, "reminders": {}, "duels": {}}


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {}

    for key, value in DEFAULT_DATA.items():
        data.setdefault(key, value)
    data.setdefault("profiles", {})
    data.setdefault("reminders", {})
    data.setdefault("duels", {})
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_text(value):
    return (value or "").strip()


def normalize_command(text):
    value = normalize_text(text)
    if value.startswith("/"):
        return value
    return value


def ensure_user(data, user_id):
    user_id = str(user_id)
    profiles = data.setdefault("profiles", {})
    profile = profiles.setdefault(
        user_id,
        {
            "name": user_id,
            "character": None,
            "hp": 100,
            "attack": 10,
            "defense": 5,
            "gold": 50,
            "wins": 0,
            "losses": 0,
        },
    )
    data.setdefault("users", [])
    if user_id not in data["users"]:
        data["users"].append(user_id)
    return profile


def find_character(name):
    query = normalize_text(name).lower()
    if not query:
        return None
    for character in CHARACTERS:
        if character["name"].lower() == query or character["name"].replace(" ", "").lower() == query.replace(" ", ""):
            return character
    for character in CHARACTERS:
        if query in character["name"].lower():
            return character
    return None


def render_help():
    return (
        "📘 راهنمای ربات آقای X\n\n"
        "دستورات اصلی:\n"
        "• /start - شروع و معرفی ربات\n"
        "• /help - نمایش راهنما\n"
        "• /ping - تست پاسخ‌دهی\n"
        "• /سوال <متن> - پاسخ هوشمند\n"
        "• /تمرین - تمرین هوش\n"
        "• /یادآوری <متن> - ثبت یادآوری\n"
        "• /شخصیت‌ها - نمایش 10 شخصیت\n"
        "• /انتخاب <نام شخصیت> - انتخاب شخصیت\n"
        "• /دور <ایدی> - شروع Duel\n"
        "• /قبول - قبول Duel\n"
        "• /status - وضعیت حساب\n\n"
        "مثال‌ها:\n"
        "• /سوال بهترین راه برای یادگیری پایتون چیست؟\n"
        "• /یادآوری فردا تمرین کدنویسی\n"
        "• /انتخاب گرگعلی\n"
        "• /دور 123456789\n"
    )


async def handle_start(update):
    user_id = str(getattr(update, "object_guid", "unknown"))
    data = load_data()
    ensure_user(data, user_id)
    save_data(data)
    await update.reply(
        "🎮 خوش اومدی! من ربات آقای X هستم.\n"
        "برای دیدن دستورات: /help\n"
        "برای انتخاب شخصیت: /شخصیت‌ها\n"
        "برای Duel: /دور <آیدی کاربر>"
    )


async def handle_ping(update):
    await update.reply("🏓 Pong! پاسخ‌گویی فعال است.")


async def handle_help(update):
    await update.reply(render_help())


async def handle_status(update):
    user_id = str(getattr(update, "object_guid", "unknown"))
    data = load_data()
    profile = ensure_user(data, user_id)
    character = profile.get("character") or "بدون شخصیت"
    await update.reply(
        f"📊 وضعیت حساب:\n"
        f"شخصیت: {character}\n"
        f"HP: {profile.get('hp', 100)}\n"
        f"ATK: {profile.get('attack', 10)}\n"
        f"DEF: {profile.get('defense', 5)}\n"
        f"طلا: {profile.get('gold', 50)}"
    )


async def handle_character_list(update):
    lines = ["🧙‍♂️ لیست شخصیت‌ها:"]
    for index, character in enumerate(CHARACTERS, start=1):
        lines.append(
            f"{index}. {character['emoji']} {character['name']} | HP {character['hp']} | ATK {character['attack']} | DEF {character['defense']}"
        )
    await update.reply("\n".join(lines))


async def handle_pick_character(update, raw_name):
    user_id = str(getattr(update, "object_guid", "unknown"))
    character = find_character(raw_name)
    if not character:
        await update.reply("❌ شخصیت پیدا نشد. از /شخصیت‌ها برای دیدن نام‌ها استفاده کن.")
        return

    data = load_data()
    profile = ensure_user(data, user_id)
    profile["character"] = character["name"]
    profile["hp"] = character["hp"]
    profile["attack"] = character["attack"]
    profile["defense"] = character["defense"]
    save_data(data)
    await update.reply(
        f"✅ شخصیت انتخاب شد: {character['emoji']} {character['name']}\n"
        f"HP: {character['hp']} | ATK: {character['attack']} | DEF: {character['defense']}"
    )


async def handle_question(update, prompt):
    if not prompt:
        await update.reply("❗ لطفاً بعد از /سوال متن سوال را بنویس.")
        return
    answer = await ask_gpt(prompt)
    await update.reply(answer)


async def handle_training(update):
    exercises = [
        "۲ + ۸ = ؟",
        "۱۲ × ۳ = ؟",
        "کدام عدد کوچکتر است؟ 15 یا 17",
        "اگر ۳ گربه ۳ روز کار کنند، چند گربه می‌سازند؟",
        "در فارسی، «دانا» به چه معنی است؟",
    ]
    question = random.choice(exercises)
    await update.reply(f"🧠 تمرین: {question}\nبرای پاسخ فقط عدد یا جمله بنویس.")


async def handle_reminder(update, reminder_text):
    if not reminder_text:
        await update.reply("❗ بعد از /یادآوری متن یادآوری را بنویس.")
        return

    data = load_data()
    user_id = str(getattr(update, "object_guid", "unknown"))
    reminders = data.setdefault("reminders", {})
    reminders.setdefault(user_id, []).append({
        "text": reminder_text,
        "created_at": datetime.now().isoformat(),
    })
    save_data(data)
    await update.reply(f"✅ یادآوری ثبت شد: {reminder_text}")


async def handle_duel_request(update, target):
    if not target:
        await update.reply("❗ برای شروع Duel بعد از /دور آیدی یا نام بازیکن را بنویس.")
        return

    user_id = str(getattr(update, "object_guid", "unknown"))
    data = load_data()
    data.setdefault("duels", {})
    data["duels"][user_id] = {"target": target, "status": "pending"}
    save_data(data)
    await update.reply(f"⚔️ درخواست Duel برای {target} ارسال شد. منتظر پاسخ است. /قبول برای قبول")


async def handle_accept_duel(update):
    user_id = str(getattr(update, "object_guid", "unknown"))
    data = load_data()
    duels = data.setdefault("duels", {})
    challenger = None
    for challenger_id, item in duels.items():
        if item.get("target") == user_id and item.get("status") == "pending":
            challenger = challenger_id
            break

    if not challenger:
        await update.reply("❌ هیچ درخواست Duel در انتظار شما نیست.")
        return

    duels[challenger]["status"] = "accepted"
    save_data(data)
    await update.reply(f"✅ Duel پذیرفته شد. بین {challenger} و {user_id}.\nبرای شروع بازی، /بازی")


async def handle_game_start(update):
    user_id = str(getattr(update, "object_guid", "unknown"))
    data = load_data()
    profile = ensure_user(data, user_id)
    if not profile.get("character"):
        await update.reply("⚠️ اول باید یک شخصیت انتخاب کنی. /انتخاب گرگعلی")
        return

    enemy = random.choice(["دشمن 1", "دشمن 2", "دشمن 3"])
    damage = max(1, int(profile.get("attack", 10)) - random.randint(0, 4))
    enemy_damage = max(1, random.randint(7, 15) - int(profile.get("defense", 5)))

    result = random.choice(["attack", "enemy"])
    if result == "attack":
        profile["gold"] = profile.get("gold", 50) + 10
        profile["wins"] = profile.get("wins", 0) + 1
        await update.reply(
            f"🎯 حمله موفق بود!\n"
            f"حریف: {enemy}\n"
            f"آسیب وارد شده: {damage}\n"
            f"پول: +10\n"
            f"ویرایش وضعیت: {profile.get('character')}"
        )
    else:
        profile["hp"] = max(0, profile.get("hp", 100) - enemy_damage)
        profile["losses"] = profile.get("losses", 0) + 1
        await update.reply(
            f"💥 حمله حریف موفق بود!\n"
            f"آسیب دریافتی: {enemy_damage}\n"
            f"HP باقی مانده: {profile.get('hp', 0)}"
        )

    save_data(data)


async def handle_message(update: Updates):
    if Client is None:
        return

    text = normalize_command(getattr(update, "text", "") or "")
    if not text:
        return

    command = text.lower()

    if command in {"/start", "start"}:
        await handle_start(update)
        return

    if command in {"/help", "help", "/کمک", "کمک"}:
        await handle_help(update)
        return

    if command in {"/ping", "ping"}:
        await handle_ping(update)
        return

    if command.startswith("/سوال"):
        prompt = text.split(None, 1)[1] if len(text.split()) > 1 else ""
        await handle_question(update, prompt)
        return

    if command.startswith("/question"):
        prompt = text.split(None, 1)[1] if len(text.split()) > 1 else ""
        await handle_question(update, prompt)
        return

    if command.startswith("/تمرین") or command.startswith("/practice"):
        await handle_training(update)
        return

    if command.startswith("/یادآوری") or command.startswith("/reminder"):
        reminder_text = text.split(None, 1)[1] if len(text.split()) > 1 else ""
        await handle_reminder(update, reminder_text)
        return

    if command.startswith("/شخصیت‌ها") or command.startswith("/characters"):
        await handle_character_list(update)
        return

    if command.startswith("/انتخاب") or command.startswith("/choose"):
        name = text.split(None, 1)[1] if len(text.split()) > 1 else ""
        await handle_pick_character(update, name)
        return

    if command.startswith("/دور") or command.startswith("/duel"):
        target = text.split(None, 1)[1] if len(text.split()) > 1 else ""
        await handle_duel_request(update, target)
        return

    if command == "/قبول":
        await handle_accept_duel(update)
        return

    if command in {"/status", "/وضعیت"}:
        await handle_status(update)
        return

    if command in {"/بازی", "/game"}:
        await handle_game_start(update)
        return

    if command in {"سلام", "hello", "hi", "هلو"}:
        await update.reply("سلام! برای دیدن دستورات /help را بزن.")
        return

    if command.startswith("/"):
        await update.reply("❌ دستور نامعتبر است. /help را ببین.")
        return

    if text == "جوک":
        await update.reply("😂 " + random.choice(jokes))
        return

    if text == "دانستنی":
        await update.reply("📚 " + random.choice(facts))
        return

    if text == "انگیزشی":
        await update.reply("🌟 " + random.choice(motivations))
        return

    if text == "ساعت":
        now = datetime.now().strftime("%H:%M:%S")
        await update.reply(f"🕰 ساعت الان: {now}")
        return

    if text == "تاریخ":
        if jdatetime:
            today = jdatetime.date.today().strftime("%Y/%m/%d")
        else:
            today = datetime.now().strftime("%Y/%m/%d")
        await update.reply(f"📅 امروز: {today}")
        return

    if text.startswith("محاسبه "):
        expr = text[8:].strip()
        try:
            result = eval(expr, {"__builtins__": None}, vars(math))
            await update.reply(f"🧮 نتیجه: {result}")
        except Exception:
            await update.reply("❌ فرمول نامعتبر است!")
        return

    if text.startswith("تکرار "):
        body = text[6:].strip()
        match = re.match(r"(.+)\s\*(\d+)$", body)
        if match:
            value, count = match.group(1).strip(), int(match.group(2))
            count = min(count, 10)
            await update.reply((value + "\n") * count)
        else:
            await update.reply("📌 فرمت درست نیست. مثال: تکرار سلام *3")
        return

    if text.startswith("پیشنهاد "):
        suggestion = text[9:].strip()
        data = load_data()
        if suggestion:
            data.setdefault("suggestions", []).append({"from": str(getattr(update, "object_guid", "unknown")), "text": suggestion})
            save_data(data)
            await update.reply("💡 پیشنهادت ثبت شد! ممنونم 🌟")
        else:
            await update.reply("بعد از 'پیشنهاد' متن را بنویس.")
        return

    if text.startswith("بات "):
        prompt = text[4:].strip()
        if prompt:
            await handle_question(update, prompt)
        else:
            await update.reply("❗ لطفاً بعد از 'بات' متن سوال را بنویس.")
        return


if Client is not None:
    bot = Client(name=BOT_NAME)
    bot.on_message_updates()(handle_message)


if __name__ == "__main__":
    if Client is None:
        raise RuntimeError("shadpy is not installed. Please install requirements.txt first.")
    bot.run()
