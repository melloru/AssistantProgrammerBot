import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from ..filters.chat_types import ChatTypeFilter
from ..services.message_service import MessageService


start_router = Router()
start_router.message.filter(ChatTypeFilter(['private']))


@start_router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer('в данном боте вы сможете:')
    await asyncio.sleep(1)
    await message.answer('задать любой вопрос, связанный с программированием.')
    await asyncio.sleep(1)
    await message.answer('помогать, отвечая на вопросы других пользователей.')
    await asyncio.sleep(1)
    await message.answer('введите команду /menu для начала работы.')


@start_router.message(Command('menu'))
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    await MessageService.send_main_menu(update=message)


@start_router.callback_query(F.data == 'main_menu')
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await MessageService.send_main_menu(update=callback)
