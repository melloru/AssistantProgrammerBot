from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from ..services.message_service import MessageService


state_management_router = Router()


@state_management_router.message(StateFilter('*'), Command('cancel'))
@state_management_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    current_state_data = await state.get_data()

    if not (current_state or current_state_data):
        await message.answer('Для разработки')
        return

    await state.clear()
    await message.answer('Сценарий отменен')
    await MessageService.send_main_menu(message)
