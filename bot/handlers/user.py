import os

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot.clients.init_clients import storage_client
from bot.states import Order
from bot.texts import START_MESSAGE, ADD_TO_CART_MESSAGE
from bot.utils import (
    make_inline_keyboard,
    UserConfirmButtons,
    confirm_order,
    make_cart_message,
)
from config import Config

user_router = Router()


@user_router.callback_query(Order.cart, F.data.in_([el.name for el in UserConfirmButtons]))
async def confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.data == UserConfirmButtons.sure.name:
        user_data = await state.get_data()
        order_message = user_data.get("cart_message")
        await confirm_order(bot, order_message)
        message = "Заказ принят, благодарю!"
    else:
        message = "Заказ отменен"

    await state.set_data({})
    await state.clear()
    await callback.message.answer(text=message)
    await callback.answer()


@user_router.message(Command(commands=["cart"]))
async def pay_order(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    cart_message = await make_cart_message(user_data)
    order_data = await state.get_data()
    order_data['cart_message'] = cart_message
    await state.update_data(order_data)

    keyboard = await make_inline_keyboard([{
        "text": button.value,
        "callback_data": button.name
    } for button in UserConfirmButtons])
    await state.set_state(Order.cart)
    await msg.answer(cart_message, reply_markup=keyboard)


@user_router.message(Order.quantity)
async def quantity_inserted(msg: Message, state: FSMContext):
    user_input = msg.text
    order_data = await state.get_data()
    callback_data = order_data["callback_data"]
    product = storage_client.revers_callbacks_dict[callback_data]
    order_data["order"][product] = int(user_input)
    await state.update_data(order_data)


@user_router.callback_query(
    StateFilter(None),
    F.data == storage_client.callbacks_dict[ADD_TO_CART_MESSAGE],
)
async def quantity_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Теперь введите необходимое количество")
    await state.set_state(Order.quantity)
    await callback.answer()


@user_router.callback_query(
    StateFilter(None),
    lambda callback: callback.data not in [el.name for el in UserConfirmButtons]
)
async def common_callback_handler(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data
    product = storage_client.revers_callbacks_dict[callback_data]
    buttons_info = [
        {
            "text": ADD_TO_CART_MESSAGE,
            "callback_data": storage_client.callbacks_dict[ADD_TO_CART_MESSAGE]["callback_data"]
        }
    ]
    photo_id = storage_client.photo_ids.get(product)
    if photo_id:
        image = photo_id
    else:
        image = FSInputFile(os.path.join(Config.IMAGES_PATH, f"{product}.jpg"))

    result = await callback.message.answer_photo(
        image,
        caption="Фото примеры",
        reply_markup=await make_inline_keyboard(buttons_info)
    )
    if not photo_id:
        storage_client.photo_ids[product] = result.photo[-1].file_id

    await state.update_data({"callback_data": callback_data, "order": {}})
    await callback.answer()


@user_router.message(StateFilter("*"), Command(commands=["start"]))
async def make_order(msg: Message, state: FSMContext):
    await state.set_data({})
    await state.clear()

    buttons_info = [
        {
            "text": product,
            "callback_data": storage_client.data[product]["callback_data"]
        }
        for product in storage_client.data.keys()
    ]

    await msg.answer(START_MESSAGE, reply_markup=await make_inline_keyboard(buttons_info))
