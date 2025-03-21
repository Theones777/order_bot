import asyncio
import traceback
from enum import Enum

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    InlineKeyboardButton, ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.clients.init_clients import storage_client
from bot.log import logger
from config import Config


class UserConfirmButtons(Enum):
    sure = "Уверен"
    cancel = "Отмена"


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Сделать заказ"),
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


async def make_order_message(order_data: dict, user_input: str):
    order_items = [storage_client.revers_callbacks_dict[callback_data] for callback_data in order_data.values()]
    order_message = "\n".join([*order_items, user_input])
    return order_message


async def confirm_order(bot: Bot, order_message: str):
    await bot.send_message(
        chat_id=Config.CHEF_TG_ID,
        text=order_message,
        reply_markup=ReplyKeyboardRemove(),
    )
