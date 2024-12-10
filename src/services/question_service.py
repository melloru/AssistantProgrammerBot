from typing import Optional, Union

from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from src.database.models import Question as QuestionModel
from .message_service import MessageService


class DictQuestion:
    """Класс для создания объекта DictQuestion из словаря"""

    def __init__(self, question_dict: dict):
        self.short_question = question_dict['short_question']
        self.full_question = question_dict['full_question']
        self.image_question = question_dict['image_question']


class QuestionService:

    @staticmethod
    async def display_question(
            update: Union[CallbackQuery, Message],
            question: Union[DictQuestion, QuestionModel],
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            additional_text: Union[str, None] = 'Ваш вопрос.',
            some_text: str = None,
    ) -> None:
        """
        Отображает вопрос в виде сообщения пользователю.

        Эта функция формирует текст сообщения, содержащего как минимум
        один из переданных вопросов (короткий, полный) и, при необходимости,
        добавляет дополнительные тексты. Если не указано другое, используется
        текст по умолчанию "Ваш вопрос".

        :param update: (Union[CallbackQuery, Message]): Объект, представляющий обновление (либо CallbackQuery, либо Message).
        :param question:
        :param reply_markup: (Optional[InlineKeyboardMarkup]): Кнопки, которые будут показаны пользователю в сообщении. Если не указано, используется меню по умолчанию.
        :param additional_text: (Optional[str]): Текст, который будет отображен перед вопросом. По умолчанию - "Ваш вопрос.".
        :param some_text: (Optional[str]): Дополнительный текст, который будет отображен после основного вопроса. Может быть None.
        """

        text = []

        if additional_text:
            text.append(f'{additional_text}\n\n\n')
        if question.short_question:
            text.append(f'{question.short_question}\n\n')
        if question.full_question:
            text.append(f'{question.full_question}')
        if some_text:
            text.append(f'\n\n\n{some_text}')

        text = ''.join(text)

        await MessageService.edit_message(update=update, text=text, reply_markup=reply_markup,
                                          photo=question.image_question)
