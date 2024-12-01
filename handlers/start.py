from aiogram import Router, types, F
from aiogram.filters import CommandStart

from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard


start_router = Router()
start_router.message.filter(ChatTypeFilter(['private']))

start_kb = get_keyboard('Как работает бот', 'Я ученик', 'Я учитель', sizes=(1, 2))


@start_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Проверка старт.', reply_markup=start_kb)

@start_router.message(F.text == 'Главное меню')
async def main_menu(message: types.Message):
    await message.answer('Переход в главное меню', reply_markup=start_kb)



