from aiogram.fsm.state import StatesGroup, State

class Order(StatesGroup):
    comments = State()
    confirm = State()
