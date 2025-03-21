from enum import Enum

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    InlineKeyboardButton, ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.clients.init_clients import storage_client
from config import Config


class UserConfirmButtons(Enum):
    sure = "Уверен"
    cancel = "Отмена"


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Сделать заказ"),
        BotCommand(command="cart", description="Корзина"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="cancel", description="Отмена"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def make_inline_keyboard(buttons_info: list) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for button_info in buttons_info:
        builder.add(
            InlineKeyboardButton(
                text=f"{button_info.get("text")}",
                callback_data=button_info.get("callback_data")
            )
        )
    return builder.as_markup()


async def make_cart_message(order_data: dict):
    result = "Ваш заказ:\n"
    amount = 0
    for product, product_count in order_data["order"].items():
        result += f"{product} - {product_count}\n"
        amount += int(storage_client.data[product]['цена']) * product_count
    result += "Сумма заказа - {amount} рублей"
    return result


async def confirm_order(bot: Bot, order_message: str):
    await bot.send_message(
        chat_id=Config.CHEF_TG_ID,
        text=order_message,
        reply_markup=ReplyKeyboardRemove(),
    )
