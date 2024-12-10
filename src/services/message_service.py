from typing import Optional, Union

from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from src.kbds.inline import start_kb


class MessageService:

    @staticmethod
    async def edit_message(
            update: Union[CallbackQuery, Message],
            text: str,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
            photo: Optional[str] = None,
    ) -> None:
        """
        Изменяет сообщение в зависимости от того, является ли оно CallbackQuery или Message.
        Удаляет предыдущее сообщение, если это необходимо.
        """

        if isinstance(update, CallbackQuery):

            message = update.message

            if message.content_type == 'text' and not photo:
                await message.edit_text(text=text, reply_markup=reply_markup)
                return

            # Удаляем предыдущее сообщение, если оно содержит фото или photo указан, либо оно Message.
            if (message.content_type == 'photo' or photo) and message:
                await update.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            await message.answer_photo(photo=photo, caption=text, reply_markup=reply_markup) if photo \
                else await message.answer(text=text, reply_markup=reply_markup)

        elif isinstance(update, Message):

            await update.answer_photo(photo=photo, caption=text, reply_markup=reply_markup) if photo \
                else await update.answer(text=text, reply_markup=reply_markup)

    @staticmethod
    async def send_main_menu(
            update: Union[CallbackQuery, Message],
            text: str = 'Что Вы хотите сделать?',
    ) -> None:
        """
        Отправляет главное меню пользователю.

        :param update: Обновление, которое может быть либо CallbackQuery, либо Message.
        :param text: Текст сообщения (по умолчанию 'Что Вы хотите сделать?').
        """
        await MessageService.edit_message(update=update, text=text, reply_markup=start_kb)
