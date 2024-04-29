from aiogram.fsm.state import StatesGroup, State


class TriggerState(StatesGroup):
    awaiting_title = State()
    awaiting_text = State()


class AddShopState(StatesGroup):
    awaiting_tittle = State()
    awaiting_description = State()
    awaiting_photo = State()


class ShopConfigurationsState(StatesGroup):
    awaiting_description = State()
    awaiting_photo = State()


class AnnounceTextState(StatesGroup):
    awaiting_announce = State()
