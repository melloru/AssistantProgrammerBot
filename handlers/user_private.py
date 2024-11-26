from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup

from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

start_kb = get_keyboard('Как работает бот', 'Мне нужна помощь', 'Я хочу помочь', sizes=(1, 2))

class StudentQuestion(StatesGroup):
    question = State()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Проверка старт', reply_markup=start_kb)

@user_private_router.message(F.text == 'Мне нужна помощь')
async def student_question(message: types.Message, state: FSMContext):
    await message.answer('Опишите свою проблему:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(StudentQuestion.question)

@user_private_router.message(F.text, StudentQuestion.question)
async def capture_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer('Ваш вопрос добавлен')
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()

