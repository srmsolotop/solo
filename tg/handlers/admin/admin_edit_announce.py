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
from ... import text
from ..shop.announces import button_texter
from aiogram.fsm.context import FSMContext
from ...states import AnnounceTextState
router = Router()


@router.callback_query(F.data.startswith("admin_editannounce_"))
async def admin_edit_announce(callback: CallbackQuery):
    data = callback.data.split("_")
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
        if user.is_admin:
            shop = await sync_to_async(Shop.objects.get)(id=data[2])
            announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            if not announces:
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            builder = InlineKeyboardBuilder()
            for num, i in enumerate(announces):
                builder.add(InlineKeyboardButton(text=f"{await button_texter(num + 1)} Анонс {'🟢' if i.on else '⚫'}",
                                                 callback_data=f"admin_changeannounce_{i.id}"))
            builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
            builder.adjust(1)
            await callback.message.delete()
            await callback.message.answer(text=text.shop_announce_text, reply_markup=builder.as_markup(),
                                                parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(e)


@router.callback_query(F.data.startswith("admin_changeannounce_"))
async def admin_change_announce(callback: CallbackQuery):
    data = callback.data.split("_")
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
        if user.is_admin:
            announce_text = await sync_to_async(AnnounceText.objects.get)(id=data[2])

    except Exception as e:
        print(e)

