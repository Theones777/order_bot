from aiogram.fsm.state import StatesGroup, State

class Order(StatesGroup):
    quantity = State()
    confirm = State()
