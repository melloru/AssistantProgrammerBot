from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def create_pagination_keyboard(page, total_pages):
    keyboard = InlineKeyboardBuilder()

    if page > 1:
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{page - 1}"))

    if page < total_pages:
        keyboard.add(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{page + 1}"))

    keyboard.add(InlineKeyboardButton(text='Удалить', callback_data='delete_'))

    return keyboard.as_markup()
