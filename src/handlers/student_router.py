from aiogram import Router, types, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..filters.chat_types import ChatTypeFilter
from ..database.orm_query import (orm_add_question, orm_add_student, orm_find_student,
                                    orm_get_student_questions, orm_delete_question)
from ..states.states import StudentQuestion
from ..kbds.inline import get_callback_btns, change_question_kb
from ..validators.question_validation import validate_short_question, validate_full_question, send_error_message
from ..services.question_service import QuestionService, DictQuestion
from ..services.message_service import MessageService


student_router = Router()
student_router.message.filter(ChatTypeFilter(['private']))


# СОЗДАНИЕ ВОПРОСА

@student_router.callback_query(StateFilter(None), F.data == 'create_question')
async def student_short_question(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Кратко опишите проблему.\nПример:\nНе получается подключиться к БД')
    await state.set_state(StudentQuestion.short_question)


@student_router.message(StudentQuestion.short_question, F.text)
async def student_short_question_callback(message: types.Message, state: FSMContext):
    short_question = message.text

    if validate_short_question(short_question):
        await send_error_message(message=message, error_key='wrong_short_question')
        return

    await state.update_data(short_question=short_question)

    question_dict = await state.get_data()

    if 'full_question' in question_dict:
        question = DictQuestion(question_dict)
        await QuestionService.display_question(message, question, reply_markup=change_question_kb)
        return

    await message.answer('Опишите проблему более подробно.')
    await state.set_state(StudentQuestion.full_question)


@student_router.message(StudentQuestion.short_question)
async def student_short_question2(message: types.Message):
    await send_error_message(message=message, error_key='wrong_short_question')


@student_router.message(StudentQuestion.full_question, F.text)
async def student_full_question(message: types.Message, state: FSMContext):
    full_question = message.text

    if validate_full_question(full_question):
        await send_error_message(message=message, error_key='wrong_full_question')
        return

    await state.update_data(full_question=full_question)

    question_dict = await state.get_data()

    if 'image_question' in question_dict:
        question = DictQuestion(question_dict)
        await QuestionService.display_question(message, question, reply_markup=change_question_kb)
        return

    await message.answer('Отправьте изображение или введите "Пропустить".')
    await state.set_state(StudentQuestion.image_question)


@student_router.message(StudentQuestion.full_question)
async def student_full_question2(message: types.Message):
    await send_error_message(message=message, error_key='wrong_full_question')


@student_router.message(StudentQuestion.image_question, or_f(F.photo, F.text.casefold() == 'пропустить'))
async def student_image(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(image_question=message.photo[-1].file_id)
    else:
        await state.update_data(image_question=None)

    question_dict = await state.get_data()

    question = DictQuestion(question_dict)
    await QuestionService.display_question(message, question, reply_markup=change_question_kb)


@student_router.message(StudentQuestion.image_question)
async def student_image(message: types.Message):
    await send_error_message(message=message, error_key='wrong_image_question')
    return



# Запись вопроса в БД

@student_router.callback_query(F.data == 'capture_question')
async def save_question(callback: CallbackQuery, state: FSMContext):
    try:
        question = await state.get_data()

        student_tg_id = callback.from_user.id
        student = await orm_find_student(student_tg_id)
        if not student:
            await callback.answer('Вы новый пользователь, теперь вы зарегистрированы.')
            student = await orm_add_student(student_tg_id)

        await orm_add_question(question['short_question'],
                               question['full_question'],
                               question['image_question'],
                               student_id=student.id)

        await callback.answer('Ваш вопрос отправлен на модерацию')
    except Exception:
        await callback.answer('Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте позже.')
    finally:
        await state.clear()
        await MessageService.send_main_menu(update=callback)



#  Изменение вопроса (ДО ЗАПИСИ В БД)

@student_router.callback_query(F.data == 'change_cur_question')
async def change_cur_question(callback: CallbackQuery):
    text = 'Что хотите изменить?'

    reply_markup = get_callback_btns(
        btns={'Вопрос': 'change_short_question',
              'Описание проблемы': 'change_full_question',
              'Фото': 'change_image_question',
              'Назад к карточке вопроса': 'back_to_card_question'},
        sizes=(2, 2)
    )

    await MessageService.edit_message(update=callback, text=text, reply_markup=reply_markup)


@student_router.callback_query(F.data == 'change_short_question')
async def change_s_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите новый короткий вопрос:')
    await state.set_state(StudentQuestion.short_question)


@student_router.callback_query(F.data == 'change_full_question')
async def change_f_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите новое полное описание:')
    await state.set_state(StudentQuestion.full_question)


@student_router.callback_query(F.data == 'change_image_question')
async def change_image(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Отправьте новое изображение или введите "Пропустить".')
    await state.set_state(StudentQuestion.image_question)



# Просмотр вопросов

@student_router.callback_query(F.data == 'show_user_questions')
async def show_short_questions(callback: types.CallbackQuery, state: FSMContext):
    """Выводит список короткой части вопросов пользователя"""
    data = await state.get_data()

    questions = await orm_get_student_questions(callback.from_user.id) if not data.get('questions') else data['questions']

    if not questions:
        await callback.answer('У вас нет вопросов.')
        return

    await state.update_data(questions=questions)

    btns = {str(i + 1): f'question_{i}' for i, _ in enumerate(questions)}
    btns['Главное меню'] = 'main_menu'

    text = '\n'.join([f'{i}) {question.short_question}' for i, question in enumerate(questions, start=1)])

    await MessageService.edit_message(update=callback, text=f'<b>Выберите вопрос.</b>\n{text}',
                                reply_markup=get_callback_btns(btns=btns))


@student_router.callback_query(F.data.startswith('question_'))
async def show_full_question(callback: CallbackQuery, state: FSMContext):
    """Выводит развернутый вопрос"""
    question_index = int(callback.data.split('_')[-1])
    questions = await state.get_value('questions')
    question = questions[question_index]

    reply_markup = get_callback_btns(
        btns={'Удалить': f'delete_question_{question_index}', 'Назад': 'show_user_questions'})
    await QuestionService.display_question(callback, question, reply_markup=reply_markup)


@student_router.callback_query(F.data.startswith('delete_question_'))
async def delete_question(callback: types.CallbackQuery, state: FSMContext):
    """Удаляет вопрос из БД"""
    data = await state.get_data()

    question_index = int(callback.data.split('_')[-1])
    questions = data['questions']

    question_for_del = questions.pop(question_index)
    await orm_delete_question(question_id=question_for_del.id)

    await MessageService.edit_message(update=callback, text='Вопрос успешно удален.', reply_markup=get_callback_btns(
        btns={'Назад к списку вопросов': 'show_user_questions',
              'Главное меню': 'main_menu'}))
