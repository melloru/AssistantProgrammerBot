import math

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard
from database.orm_query import orm_add_question, orm_add_student, orm_find_student, orm_get_student_questions, \
    orm_delete_question
from utils.user_operations import get_user_tg_id
from kbds.inline import create_pagination_keyboard
from utils.paginator import Paginator

student_router = Router()
student_router.message.filter(ChatTypeFilter(['private']))

student_kb = get_keyboard('Задать вопрос', 'Мои вопросы', 'Главное меню', sizes=(2, 1))


class StudentQuestion(StatesGroup):
    question = State()

@student_router.message(F.text == 'Я ученик')
async def student_question(message: types.Message):
    await message.answer('Что Вы хотите сделать?', reply_markup=student_kb)


@student_router.message(StateFilter(None), F.text == 'Задать вопрос')
async def student_question(message: types.Message, state: FSMContext):
    await message.answer('Опишите свою проблему:', reply_markup=get_keyboard('Отмена'))
    await state.set_state(StudentQuestion.question)


@student_router.message(StateFilter('*'), Command('cancel'))
@student_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Сценарий отменен', reply_markup=student_kb)


@student_router.message(F.text, StudentQuestion.question)
async def capture_question(message: types.Message, state: FSMContext):
    try:
        await state.update_data(question=message.text)
        await message.answer('Ваш вопрос отправлен на модерацию.', reply_markup=student_kb)

        data = await state.get_data()
        user_tg_id = await get_user_tg_id(message)
        student = await orm_find_student(student_tg_id=user_tg_id)
        if not student:
            await message.answer('Вы новый пользователь, теперь вы зарегистрированы.')
            student = await orm_add_student(student_tg_id=user_tg_id)
        await orm_add_question(question_text=data['question'], student_id=student.id)
    except Exception as e:
        await message.answer('Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте позже.')
    finally:
        await state.clear()


@student_router.message(F.text == 'Мои вопросы')
async def show_student_questions(message: types.Message, state: FSMContext):
    questions = await orm_get_student_questions(message.from_user.id)

    if not questions:
        await message.answer("У вас нет вопросов.")
        return

    paginator = Paginator(questions)
    await state.update_data(paginator=paginator)

    qstn = paginator.get_page()[0]
    response_text = f'{qstn.question_text}'

    keyboard = create_pagination_keyboard(paginator.cur_page, paginator.total_pages)

    await message.answer(response_text, reply_markup=keyboard)


@student_router.callback_query(F.data.startswith('prev_') | F.data.startswith('next_') | F.data.startswith('delete_'))
async def paginate_questions(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    paginator = user_data.get('paginator')

    page = paginator.cur_page

    if callback_query.data.startswith('delete_'):
        del_qstn = paginator.items.pop(page - 1)
        await orm_delete_question(del_qstn.id)
        paginator.total_pages = math.ceil(len(paginator.items) / paginator.per_page)
        if page > paginator.total_pages:
            page -= 1

    elif callback_query.data.startswith("prev_"):
        page -= 1
    else:
        page += 1

    paginator.cur_page = page

    if not len(paginator.items):
        await callback_query.message.edit_text('Нет вопросов для отображения.')
        return
    elif page < 1 or page > paginator.total_pages:
        await callback_query.answer("Нет таких страниц.")
        return

    qstn = paginator.get_page()[0]
    response_text = f'{qstn.question_text}'


    keyboard = create_pagination_keyboard(paginator.cur_page, paginator.total_pages)


    await callback_query.message.edit_text(response_text, reply_markup=keyboard)
    await callback_query.answer()
