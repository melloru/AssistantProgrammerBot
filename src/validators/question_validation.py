from aiogram.types import Message


ERROR_MESSAGES = {
    'wrong_short_question': 'Вопрос должен содержать 15 - 100 символов. Пожалуйста, попробуйте еще раз.',
    'wrong_full_question': 'Описание проблемы должно содержать 50 - 300 символов. Пожалуйста, попробуйте еще раз.',
    'wrong_image_question': 'Вы отправили не допустимые данные, приложите фото или введите "Пропустить".',
}


def validate_short_question(short_question):
    if 15 <= len(short_question) <= 100:
        return False
    return True


def validate_full_question(full_question):
    if 50 <= len(full_question) <= 300:
        return False
    return True


async def send_error_message(message: Message, error_key: str):
    await message.answer(ERROR_MESSAGES[error_key])
