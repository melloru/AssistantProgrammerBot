import asyncio
from gc import callbacks

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter
from utils.user_operations import send_main_menu, delete_message


start_router = Router()
start_router.message.filter(ChatTypeFilter(['private']))


@start_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('в данном боте вы сможете:')
    await asyncio.sleep(2)
    await message.answer('задать любой вопрос, связанный с программированием.')
    await asyncio.sleep(2)
    await message.answer('помогать, отвечая на вопросы других пользователей.')
    await asyncio.sleep(2)
    await message.answer('введите команду /menu для начала работы.')


@start_router.message(Command('menu'))
async def main_menu(message: types.Message, state: FSMContext):
    await delete_message(message=message, state=state)
    await state.clear()
    await send_main_menu(message=message)


@start_router.callback_query(F.data == 'main_menu_')
async def main_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_main_menu(callback_query_edit=callback_query)



