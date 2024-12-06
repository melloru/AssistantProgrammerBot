import math
import asyncio

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.util import await_only

from database.models import Student
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard
from database.orm_query import orm_add_question, orm_add_student, orm_find_student, orm_get_student_questions, \
    orm_delete_question
from utils.user_operations import get_user_tg_id, send_main_menu, delete_message
from kbds.inline import create_pagination_keyboard, get_callback_btns, start_kb
from utils.paginator import Paginator

student_router = Router()
student_router.message.filter(ChatTypeFilter(['private']))


class StudentQuestion(StatesGroup):
    short_question = State()
    full_question = State()
    image = State()
    checking_the_question = State()

    texts = {
        'StudentQuestion:short_question': 'Заново введите короткий вопрос.',
        'StudentQuestion:full_question': 'Заново опишите проблему.',
        'StudentQuestion:image': 'Заново вставьте фото или введите "Пропустить".',
    }

    validation = {
        'wrong_s_qstn': 'Вопрос должен содержать 15 - 100 символов. Пожалуйста, попробуйте еще раз.',
        'wrong_f_qstn': 'Описание проблемы должно содержать 50 - 300 символов. Пожалуйста, попробуйте еще раз.',
        'wrong_image': 'Вы отправили не допустимые данные, приложите фото или введите "Пропустить".',
    }


async def show_result_card(message: types.Message, question):
    """Выводит итоговый вопрос пользователя"""
    photo = question.get('image')
    text = f'<b>Проверьте свой вопрос.</b>\n\n{question["short_question"]}\n\n{question["full_question"]}'
    kb = get_callback_btns(btns={'Продолжить': 'capture_qstn_', 'Изменить': 'change_cur_qstn_'})
    if photo:
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb)
    else:
        await message.answer(text=text, reply_markup=kb)


@student_router.message(StateFilter("*"), Command("назад"))
@student_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == StudentQuestion.short_question:
        await message.answer(
            'Предидущего шага нет, или введите свой вопрос или напишите "отмена"'
        )
        return

    previous = None
    for step in StudentQuestion.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f'Вы вернулись к прошлому шагу \n {StudentQuestion.texts[previous.state]}'
            )
            return
        previous = step


@student_router.callback_query(StateFilter(None), F.data == 'create_qstn_')
async def student_short_question(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Кратко опишите проблему.\nПример:\nНе получается подключиться к БД')
    await state.set_state(StudentQuestion.short_question)


@student_router.message(StudentQuestion.short_question, F.text)
async def student_short_question_callback(message: types.Message, state: FSMContext):
    short_question = message.text

    if len(short_question) <= 15 or len(short_question) > 100:
        error = StudentQuestion.validation['wrong_s_qstn']
        await message.answer(error)
        return

    await state.update_data(short_question=short_question)

    data = await state.get_data()

    if data.get('full_question'):
        await show_result_card(message=message, question=data)
        return


    await message.answer('Опишите проблему более подробно.')
    await state.set_state(StudentQuestion.full_question)


@student_router.message(StudentQuestion.short_question)
async def student_short_question2(message: types.Message):
    await message.answer(StudentQuestion.validation['wrong_s_qstn'])


@student_router.message(StudentQuestion.full_question, F.text)
async def student_full_question(message: types.Message, state: FSMContext):
    full_question = message.text

    if len(full_question) <= 50 or len(full_question) > 300:
        error = StudentQuestion.validation['wrong_f_qstn']
        await message.answer(error)
        return

    await state.update_data(full_question=full_question)

    data = await state.get_data()

    if 'image' in data:
        await show_result_card(message, data)
        return

    await message.answer('Отправьте изображение или введите "Пропустить".')

    await state.set_state(StudentQuestion.image)


@student_router.message(StudentQuestion.full_question)
async def student_full_question2(message: types.Message):
    await message.answer(StudentQuestion.validation['wrong_f_qstn'])


@student_router.message(StudentQuestion.image, or_f(F.photo, F.text.casefold() == 'пропустить'))
async def student_image(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await state.update_data(image=None)

    data = await state.get_data()
    await show_result_card(message, data)


@student_router.message(StudentQuestion.image)
async def student_image(message: types.Message):
    await message.answer(StudentQuestion.validation['wrong_image'])
    return


@student_router.callback_query(F.data == 'capture_qstn_')
async def capture_question(callback_query: CallbackQuery, state: FSMContext):
    try:
        qstn = await state.get_data()

        user_tg_id = await get_user_tg_id(callback_query)
        student = await orm_find_student(student_tg_id=user_tg_id)
        if not student:
            await callback_query.answer('Вы новый пользователь, теперь вы зарегистрированы.')
            student = await orm_add_student(student_tg_id=user_tg_id)

        await orm_add_question(question_text=(qstn['short_question'], qstn['full_question']), image=qstn['image'],
                               student_id=student.id)
        await callback_query.answer('Ваш вопрос отправлен на модерацию')
        await asyncio.sleep(1)
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.answer('Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте позже.')
    finally:
        await state.clear()
        await send_main_menu(callback_query_create=callback_query)


@student_router.callback_query(F.data == 'change_cur_qstn_')
async def change_cur_question(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer('Что хотите изменить?', reply_markup=get_callback_btns(
        btns={'Вопрос': 'change_s_qstn_', 'Описание проблемы': 'change_f_qstn_', 'Фото': 'change_image_',
              'Назад к карточке вопроса': 'back_'},
        sizes=(2, 2)
    ))


@student_router.callback_query(F.data == 'change_s_qstn_')
async def change_s_qstn(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Введите новый короткий вопрос:')
    await state.set_state(StudentQuestion.short_question)


@student_router.callback_query(F.data == 'change_f_qstn_')
async def change_f_qstn(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Введите новое полное описание:')
    await state.set_state(StudentQuestion.full_question)


@student_router.callback_query(F.data == 'change_image_')
async def change_image(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Отправьте новое изображение или введите "Пропустить".')
    await state.set_state(StudentQuestion.image)


@student_router.callback_query(F.data == 'show_user_questions')
async def show_student_questions(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    questions = await orm_get_student_questions(callback_query.from_user.id) if not data.get('questions') else data['questions']

    await state.update_data(questions=questions)

    if not questions:
        await callback_query.answer('У вас нет вопросов.')
        return

    btns = {str(i + 1): f'question_{i}' for i, _ in enumerate(questions)}
    print(btns)
    btns['Главное меню'] = 'main_menu_'

    choice_question_kb = get_callback_btns(btns=btns)

    text = '\n'.join([f'{i}) {question.short_question}' for i, question in enumerate(questions, start=1)])

    if await delete_message(callback_query=callback_query, state=state):
        await callback_query.message.answer(f'<b>Выберите вопрос.</b>\n{text}', reply_markup=choice_question_kb)
        return
    await callback_query.message.edit_text(f'<b>Выберите вопрос.</b>\n{text}', reply_markup=choice_question_kb)


@student_router.callback_query(F.data.startswith('question_'))
async def show_expanded_question(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    question_index = int(callback_query.data.split('_')[-1])
    questions = await state.get_value('questions')
    question = questions[question_index]
    photo = question.image
    await callback_query.message.delete()
    text = f'{question.short_question}\n\n{question.full_question}'
    kb = get_callback_btns(btns={'Удалить': f'delete_question_{question_index}', 'Назад': 'show_user_questions'})

    if photo:
        for_delete_msg = await callback_query.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
        await state.update_data(message_id_del=for_delete_msg.message_id)
    else:
        await callback_query.message.answer(text=text, reply_markup=kb)


@student_router.callback_query(F.data.startswith('delete_question_'))
async def delete_question(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    question_index = int(callback.data.split('_')[-1])
    questions = data['questions']

    question_for_del = questions.pop(question_index)

    await orm_delete_question(question_id=question_for_del.id)
    if await delete_message(callback_query=callback, state=state):
        await callback.message.answer('Вопрос успешно удален.', reply_markup=get_callback_btns(
            btns={'Назад к списку вопросов': 'show_user_questions',
                  'Главное меню': 'main_menu_'}))
    else:
        await callback.message.edit_text('Вопрос успешно удален.', reply_markup=get_callback_btns(btns={'Назад к списку вопросов': 'show_user_questions',
                                                                                                 'Главное меню': 'main_menu_'}))



# @student_router.callback_query(
#     F.data.startswith('student_prev_') | F.data.startswith('student_next_') | F.data.startswith('student_delete_'))
# async def paginate_questions(callback_query: types.CallbackQuery, state: FSMContext):
#     user_data = await state.get_data()
#     paginator = user_data.get('paginator')
#
#     page = paginator.cur_page
#
#     if callback_query.data.startswith('student_delete_'):
#         del_qstn = paginator.items.pop(page - 1)
#         await orm_delete_question(del_qstn.id)
#         paginator.total_pages = math.ceil(len(paginator.items) / paginator.per_page)
#         if page > paginator.total_pages:
#             page -= 1
#
#     elif callback_query.data.startswith("student_prev_"):
#         page -= 1
#     else:
#         page += 1
#
#     paginator.cur_page = page
#
#     if not len(paginator.items):
#         await callback_query.answer('Нет вопросов для отображения.')
#         await send_main_menu(callback_query=callback_query)
#         return
#     elif page < 1 or page > paginator.total_pages:
#         await callback_query.answer("Нет таких страниц.")
#         return
#
#     qstn = paginator.get_page()[0]
#     response_text = f'{qstn.question_text}'
#
#     keyboard = create_pagination_keyboard(paginator.cur_page, paginator.total_pages, user_type='student')
#
#     await callback_query.message.edit_text(response_text, reply_markup=keyboard)
#     await callback_query.answer()
