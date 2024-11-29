import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from common.bot_cmds_list import private
from handlers.student import student_router
from database.engine import create_db, drop_db


bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()

dp = Dispatcher(storage=storage)
dp.include_router(student_router)

async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()
    print("Бот запущен!")


async def on_shutdown(bot):
    print("Бот останавливается...")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(str(e))
