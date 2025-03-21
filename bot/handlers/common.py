from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.texts import HELP_MESSAGE
common_router = Router()


@common_router.message(StateFilter("*"), Command("help"))
async def message_help_handler(msg: Message, state: FSMContext):
    await state.set_data({})
    await state.clear()
    await msg.answer(HELP_MESSAGE)


@common_router.message(StateFilter("*"), Command(commands=["cancel"]))
async def cancel_handler(msg: Message, state: FSMContext):
    await state.set_data({})
    await state.clear()
    await msg.answer("Сброс состояния", reply_markup=ReplyKeyboardRemove())
