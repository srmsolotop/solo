from aiogram import Router, F
from asgiref.sync import sync_to_async
from ... import text
from ...models import Shop, TelegramUser, AnnounceText
from aiogram import types
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from ..shop.shop_stats import shop_statistics_generator
from aiogram.utils.keyboard import InlineKeyboardBuilder


from ...states import AnnounceTextState
router = Router()


@router.callback_query(F.data == "all_shops")
async def admin_panel_shops(callback: CallbackQuery, bot: Bot):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
    if user.is_admin:
        buffer = await shop_statistics_generator()
        input_file = types.BufferedInputFile(buffer.getvalue(), filename="chart.png")
        shops = await sync_to_async(Shop.objects.all)()
        builder = InlineKeyboardBuilder()
        for i in shops:
            builder.add(InlineKeyboardButton(text=f"{i.title}", callback_data=f"admin_editshop_{i.id}"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
        builder.adjust(1)
        await callback.message.delete()
        await bot.send_photo(chat_id=callback.message.chat.id, photo=input_file, caption=text.admin_panel_shops,
                             reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data.startswith("admin_editshop_"))
async def admin_edit_shop(callback: CallbackQuery, edit=False):
    data = callback.data.split("_")
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
        if user.is_admin:
            shop = await sync_to_async(Shop.objects.get)(id=data[2])
            builder = InlineKeyboardBuilder()
            announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            if announces:
                builder.add(InlineKeyboardButton(text="🗣 Анонсы [В разработке]", callback_data=f"admin_editannounce_{shop.id}"))
            builder.add(InlineKeyboardButton(text="⚙ Конфигурации [В раз...]", callback_data=f"admin_editconf_{shop.id}"))
            builder.add(InlineKeyboardButton(text="🛒 Ассортимент", callback_data=f"admin_editassort_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"Пауза {'🟢' if shop.paused else '⚫'}", callback_data=f"admin_pauseshop_{shop.id}"))
            builder.adjust(1)
            if not edit:
                await callback.message.answer("text", reply_markup=builder.as_markup())
            if edit:
                await callback.message.edit_text("text", reply_markup=builder.as_markup())
    except Exception as e:
        print(e)


@router.callback_query(F.data.startswith("admin_editannounce_"))
async def admin_edit_announce(callback: CallbackQuery):
    data = callback.data.split("_")
    try:
        ...
    except Exception as e:
        print()


@router.callback_query(F.data.startswith("admin_pauseshop_"))
async def admin_pause_shop(callback: CallbackQuery):
    data = callback.data.split("_")
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
        if user.is_admin:
            shop = await sync_to_async(Shop.objects.get)(id=data[2])
            if shop.paused:
                shop.paused = False
            elif not shop.paused:
                shop.paused = True
            shop.save(update_fields=['paused'])
            await admin_edit_shop(callback, edit=True)
    except Exception as e:
        print(e)


@router.callback_query(F.data.startswith("admin_editassort_"))
async def admin_edit_assorts(callback: CallbackQuery):
    data = callback.data.split("_")
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
        if user.is_admin:
            shop = await sync_to_async(Shop.objects.get)(id=data[2])
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text=f"🌳 Шишки {'⚫' if not shop.shish else '🟢'}",
                                             callback_data=f"admin_changeassort_shish_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"🍫 Гашиш{'⚫' if not shop.hash else '🟢'}",
                                             callback_data=f"admin_changeassort_hash_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"👅 LSD {'⚫' if not shop.lsd else '🟢'}",
                                             callback_data=f"admin_changeassort_lsd_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"🍄 Грибы {'⚫' if not shop.grib else '🟢'}",
                                             callback_data=f"admin_changeassort_grib_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"🍩 Каннаfood {'⚫' if not shop.shish else '🟢'}",
                                             callback_data=f"admin_changeassort_food_{shop.id}"))
            builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_admin_edit_shop"))
            builder.adjust(1)
    except Exception as e:
        print(e)


@router.callback_query(F.data == "back_to_admin_edit_shop")
async def back_to_admin_edit_shop(callback: CallbackQuery):
    await admin_edit_shop(callback, edit=True)
