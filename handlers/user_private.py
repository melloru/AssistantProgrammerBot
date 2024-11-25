from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

start_kb = get_keyboard('Как работает бот', 'Мне нужна помощь', 'Я хочу помочь', sizes=(1, 2))

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Проверка старт', reply_markup=start_kb)




