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


# def create_pagination_keyboard(page, total_pages, btns: dict = None):
#     keyboard = InlineKeyboardBuilder()
#
#     if page > 1:
#         keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{page - 1}"))
#
#     if page < total_pages:
#         keyboard.add(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{page + 1}"))
#
#     if btns:
#         for btn, data in btns.items():
#             keyboard.add(InlineKeyboardButton(text=btn, callback_data=data))
#
#     return keyboard.as_markup()

def add_pagination_buttons(keyboard, user_type, page, total_pages):
    if page > 1:
        keyboard.add(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"{user_type}_prev_{page - 1}"
        ))

    if page < total_pages:
        keyboard.add(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"{user_type}_next_{page + 1}"
        ))

    if user_type == 'student':
        keyboard.add(InlineKeyboardButton(
            text='Удалить',
            callback_data=f'{user_type}_delete_'
        ))
    elif user_type == 'teacher':
        keyboard.add(InlineKeyboardButton(
            text='Ответить',
            callback_data=f"{user_type}_answer_"
        ))

    keyboard.add(InlineKeyboardButton(
        text='Главное меню',
        callback_data=f"main_menu_"
    ))

def create_pagination_keyboard(page, total_pages, user_type, btns: dict = None, sizes=(2, 1)):
    keyboard = InlineKeyboardBuilder()

    # Вызов функции для добавления кнопок пагинации
    add_pagination_buttons(keyboard, user_type, page, total_pages)

    if btns:
        for btn, data in btns.items():
            keyboard.add(InlineKeyboardButton(text=btn, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


start_kb = get_callback_btns(btns={
    'Ответить на вопрос': 'answer_',
    'Задать вопрос': 'create_question',
    'Помощь': 'help_',
    'Посмотреть мои вопросы': 'show_user_questions'},
    sizes=(2, 2)
)

change_question_kb = get_callback_btns(btns={'Продолжить': 'capture_question', 'Изменить': 'change_cur_question'})
