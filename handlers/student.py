from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard
from database.orm_query import orm_add_question, orm_add_student, orm_find_student
from common.utils import get_user_tg_id

student_router = Router()
student_router.message.filter(ChatTypeFilter(['private']))

start_kb = get_keyboard('Как работает бот', 'Мне нужна помощь', 'Я хочу помочь', sizes=(1, 2))

class StudentQuestion(StatesGroup):
    question = State()


@student_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Проверка старт.', reply_markup=start_kb)

@student_router.message(F.text == 'Мне нужна помощь')
async def student_question(message: types.Message, state: FSMContext):
    await message.answer('Опишите свою проблему:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(StudentQuestion.question)

@student_router.message(F.text, StudentQuestion.question)
async def capture_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer('Ваш вопрос отправлен на модерацию.')
    data = await state.get_data()
    user_tg_id = await get_user_tg_id(message)
    student = await orm_find_student(student_tg_id=user_tg_id)
    if not student:
        await message.answer('Вы новый пользователь, теперь вы зарегистрированы.')
        student = await orm_add_student(student_tg_id=user_tg_id)
    await orm_add_question(question_text=data['question'], student_id=student.id)
    await message.answer(str(data))
    await state.clear()

