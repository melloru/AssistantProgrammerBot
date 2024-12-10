from aiogram import Router

from src.filters.chat_types import ChatTypeFilter

# from utils.user_operations import send_main_menu

teacher_router = Router()
teacher_router.message.filter(ChatTypeFilter(['private']))

#
#
# @teacher_router.callback_query(F.data == 'answer_')
# async def teacher_help(callback_query: types.CallbackQuery, state: FSMContext):
#     questions = await orm_get_questions()
#
#     if not questions:
#         await callback_query.answer("Нет активных вопросов")
#         return
#
#     paginator = Paginator(questions)
#     await state.update_data(paginator=paginator)
#
#     qstn = paginator.get_page()[0]
#     response_text = f'{qstn.question_text}'
#
#     keyboard = create_pagination_keyboard(paginator.cur_page, paginator.total_pages, user_type='teacher')
#
#     await callback_query.message.edit_text(response_text, reply_markup=keyboard)
#
# @teacher_router.callback_query(F.data.startswith('teacher_prev_') | F.data.startswith('teacher_next_') | F.data.startswith('teacher_answer_'))
# async def paginate_questions(callback_query: types.CallbackQuery, state: FSMContext):
#     user_data = await state.get_data()
#
#     paginator = user_data.get('paginator')
#
#     page = paginator.cur_page
#
#     if callback_query.data.startswith('teacher_prev_'):
#         page -= 1
#     elif callback_query.data.startswith('teacher_next_'):
#         page += 1
#
#     paginator.cur_page = page
#
#     if not len(paginator.items):
#         await callback_query.answer('Нет вопросов для отображения.')
#         await send_main_menu(callback_query=callback_query)
#         return
#     elif page < 1 or page > paginator.total_pages:
#         await callback_query.answer('Нет таких страниц.')
#         return
#
#     qstn = paginator.get_page()[0]
#     response_text = f'{qstn.question_text}'
#
#     keyboard = create_pagination_keyboard(paginator.cur_page, paginator.total_pages, user_type='teacher')
#
#     await callback_query.message.edit_text(response_text, reply_markup=keyboard)
#     await callback_query.answer()
#
#
# # @teacher_router.callback_query(F.data == 'teacher_answer_')
# # async def answer_to_question(callback_query: CallbackQuery, state: FSMContext):
#
