from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from filters.chat_types import ChatTypeFilter


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Проверка старт')
