import os

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile

from bot.clients.init_clients import storage_client
from bot.states import Order
from bot.texts import START_MESSAGE, CONFIRM_MESSAGE, READY_MESSAGE
from bot.utils import (
    make_inline_keyboard,
    UserConfirmButtons,
    confirm_order,
    make_order_message,
)
from config import Config

user_router = Router()


@user_router.callback_query(Order.confirm, F.data.in_([el.name for el in UserConfirmButtons]))
async def confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.data == UserConfirmButtons.sure.name:
        user_data = await state.get_data()
        order_message = user_data.get("order_message")
        await confirm_order(bot, order_message)
        message = "Заказ принят, благодарю!"
    else:
        message = "Заказ отменен"

    await state.set_data({})
    await state.clear()
    await callback.message.answer(text=message)
    await callback.answer()


@user_router.message(Order.comments)
async def comments_inserted(msg: Message, state: FSMContext):
    user_input = msg.text
    order_data = await state.get_data()
    order_message = await make_order_message(order_data, user_input)
    await state.update_data(order_message=order_message)

    await state.set_state(Order.confirm)
    keyboard = await make_inline_keyboard([{
        "text": button.value,
        "callback_data": button.name
    } for button in UserConfirmButtons])
    message = f"Вы уверены, что хотите отправить данную информацию?\n\n{order_message}"
    await msg.answer(text=message, reply_markup=keyboard)


@user_router.callback_query(
    StateFilter(None),
    F.data == storage_client.callbacks_dict[CONFIRM_MESSAGE],
)
async def ready_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=READY_MESSAGE)
    await state.set_state(Order.comments)
    await callback.answer()


@user_router.callback_query(
    StateFilter(None),
    lambda callback: callback.data not in [el.name for el in UserConfirmButtons]
)
async def common_callback_handler(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data
    step = await storage_client.find_step(callback_data)
    order_data = await state.get_data()
    order_data[step] = callback_data
    await state.update_data(order_data)
    await callback.answer("Принято")


@user_router.message(StateFilter("*"), Command(commands=["start"]))
async def make_order(msg: Message, state: FSMContext):
    await state.set_data({})
    await state.clear()

    await msg.answer(START_MESSAGE, reply_markup=ReplyKeyboardRemove())
    for step, step_info in storage_client.data.items():
        buttons_info = [
            {
                "text": text,
                "callback_data": storage_client.callbacks_dict[text]
            }
            for text in step_info
        ]
        photo_id = storage_client.photo_ids[step]
        if photo_id:
            image = photo_id
        else:
            image = FSInputFile(os.path.join(Config.IMAGES_PATH, f"{step}.jpg"))

        result = await msg.answer_photo(
            image,
            caption=f"Примеры {storage_client.steps_name[step]}",
            reply_markup=await make_inline_keyboard(buttons_info)
        )
        if not photo_id:
            storage_client.photo_ids[step] = result.photo[-1].file_id

    buttons_info = [
        {
            "text": CONFIRM_MESSAGE,
            "callback_data": storage_client.callbacks_dict[CONFIRM_MESSAGE]
        }
    ]
    await msg.answer("По готовности нажмите на кнопку ниже", reply_markup=await make_inline_keyboard(buttons_info))
