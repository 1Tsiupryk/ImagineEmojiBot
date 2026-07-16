from aiogram.fsm.state import State, StatesGroup

class EmojiCreation(StatesGroup):
    waiting_for_image = State()
    choosing_background = State()
    waiting_for_size = State()
    processing = State()