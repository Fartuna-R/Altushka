# bot.py
from aiogram import Bot, Dispatcher, types
import asyncio
import config
from utils import load_memory, save_memory
from handlers import vika_reply
import re
import random

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

# Получаем объект бота заранее
async def get_bot_me():
    return await bot.get_me()

async def vika_respond(message: types.Message):
    if not message.text:
        return

    bot_me = await get_bot_me()  # объект бота
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    print(f"услышала: {message.text}")

    # --- проверка команды /mystats ---
    if re.search(r"/mystats", message.text.lower()):
        memory = load_memory()
        user_msgs = memory.get("users", {}).get(user_name, [])
        word_stats = {}
        for msg in user_msgs:
            for w in msg.split():
                word_stats[w] = word_stats.get(w, 0) + 1

        top_words = sorted(word_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_words_text = "\n".join([f"{w}: {c}" for w, c in top_words]) if top_words else "пока нет слов"
        hearts_count = memory.get("hearts", {}).get(user_name, 0)
        stats_text = (
            f"📊 Статистика для {user_name}:\n"
            f"Сообщений: {len(user_msgs)}\n"
            f"Топ слов 5: {top_words_text}"
            f"\n❤️ Сердечек от Вики: {hearts_count}"
        )
        await message.reply(stats_text)
        return

    # --- если сообщение — ответ на Вику ---
    if message.reply_to_message and message.reply_to_message.from_user.id == bot_me.id:
        reply = vika_reply(message.text, username=user_name)
        await message.reply(reply)
    else:
        # Вика реагирует на любые сообщения
        reply = vika_reply(message.text, username=user_name)
        await message.reply(reply)

async def main():
    dp.message.register(vika_respond)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Started")
    asyncio.run(main())
