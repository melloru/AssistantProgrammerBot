from aiogram import types


async def get_user_tg_id(message: types.Message):
    return message.from_user.id
