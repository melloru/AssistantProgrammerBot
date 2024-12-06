from aiogram import types
from aiogram.fsm.context import FSMContext

from kbds.inline import start_kb


async def get_user_tg_id(request: types.Message | types.CallbackQuery):
    return request.from_user.id


async def send_main_menu(message: types.Message = None, callback_query_edit: types.CallbackQuery = None, callback_query_create: types.CallbackQuery = None, text: str = None):
    if not text:
        text = 'Что Вы хотите сделать?'

    if message:
        await message.answer(text, reply_markup=start_kb)
    elif callback_query_edit:
        await callback_query_edit.message.edit_text(text, reply_markup=start_kb)
    elif callback_query_create:
        await callback_query_create.message.answer(text, reply_markup=start_kb)


async def delete_message(state: FSMContext, callback_query: types.CallbackQuery = None, message: types.Message = None):
    data = await state.get_data()
    if data.get('message_id_del'):
        message_id = data.get('message_id_del')
        chat_id = callback_query.message.chat.id if callback_query else message.chat.id
        if callback_query:
            await callback_query.bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await state.update_data(message_id_del=None)
        return True

    return False
