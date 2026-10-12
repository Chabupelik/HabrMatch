import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

dp = Dispatcher()


@dp.message()
async def echo(message: Message):
    await message.answer("Бот HabrSwipe на связи!")


async def main():
    if not BOT_TOKEN:
        logging.warning("BOT_TOKEN не задан! Бот запущен в режиме ожидания.")
        while True:
            await asyncio.sleep(3600)

    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
