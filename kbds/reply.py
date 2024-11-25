from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton


def get_keyboard(*btns: str, sizes: (int,) = (2,), placeholder: str = None):

    keyboard = ReplyKeyboardBuilder()

    for text in btns:
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True,
                                             input_field_placeholder=placeholder)
