from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

admin_panel = [
    [InlineKeyboardButton(text="🏪 Магазины", callback_data="all_shops")],
    # [InlineKeyboardButton(text="")]
]
# admin_panel = [
#     [InlineKeyboardButton(text="Добавить триггер", callback_data="add_trigger"),
#      InlineKeyboardButton(text="Удалить триггер", callback_data="del_trigger")],
#     [InlineKeyboardButton(text="Добавить магазин", callback_data="add_shop"),
#      InlineKeyboardButton(text="Удалить магазин", callback_data="del_shop")]]


admin_panel = InlineKeyboardMarkup(inline_keyboard=admin_panel)


shop_panel = [
    [InlineKeyboardButton(text="📊 Статистика", callback_data="shop_statistics")],
     [InlineKeyboardButton(text="🗣 Анонс", callback_data="shop_announce")],
    [InlineKeyboardButton(text="⚙ Мои конфигурации", callback_data="shop_conf")],
    [InlineKeyboardButton(text="🛒 Ассортименты", callback_data="shop_assorts")]
]
shop_panel = InlineKeyboardMarkup(inline_keyboard=shop_panel)
