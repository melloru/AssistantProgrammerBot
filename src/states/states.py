from aiogram.fsm.state import StatesGroup, State


class StudentQuestion(StatesGroup):
    short_question = State()
    full_question = State()
    image_question = State()

    texts = {
        'StudentQuestion:short_question': 'Заново введите короткий вопрос.',
        'StudentQuestion:full_question': 'Заново опишите проблему.',
        'StudentQuestion:image_question': 'Заново вставьте фото или введите "Пропустить".',
    }

    validation = {
        'wrong_short_question': 'Вопрос должен содержать 15 - 100 символов. Пожалуйста, попробуйте еще раз.',
        'wrong_full_question': 'Описание проблемы должно содержать 50 - 300 символов. Пожалуйста, попробуйте еще раз.',
        'wrong_image_question': 'Вы отправили не допустимые данные, приложите фото или введите "Пропустить".',
    }
