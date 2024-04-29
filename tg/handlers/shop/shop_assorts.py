from aiogram import Router, F
from asgiref.sync import sync_to_async
from ...models import Shop, TelegramUser
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ... import text
router = Router()


@router.callback_query(F.data == "shop_assorts")
async def shop_assorts(callback: CallbackQuery, edit=None):
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
        if user.is_shop:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text=f"🌳 Шишки {'⚫' if not shop.shish else '🟢'}", callback_data=f"shop_change_shish_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"🍫 Гашиш{'⚫' if not shop.hash else '🟢'}", callback_data=f"shop_change_hash_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"👅 LSD {'⚫' if not shop.lsd else '🟢'}", callback_data=f"shop_change_lsd_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"🍄 Грибы {'⚫' if not shop.grib else '🟢'}", callback_data=f"shop_change_grib_{shop.id}"))
            builder.add(InlineKeyboardButton(text=f"🍩 Каннаfood {'⚫' if not shop.shish else '🟢'}", callback_data=f"shop_change_food_{shop.id}"))
            builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
            builder.adjust(1)
            if not edit:
                await callback.message.delete()
                await callback.message.answer(text=text.shop_assorts_text, reply_markup=builder.as_markup())
            if edit:
                await callback.message.edit_text(text=text.shop_assorts_text, reply_markup=builder.as_markup())
    except Exception as e:
        print(e)


@router.callback_query(F.data.startswith("shop_change_"))
async def shop_assort_changer(callback: CallbackQuery):
    try:
        data = callback.data.split("_")
        shop_id = data[3]
        shop = await sync_to_async(Shop.objects.get)(id=shop_id)
        if data[2] == "shish":
            shop.shish = True if not shop.shish else False
        if data[2] == "hash":
            shop.hash = True if not shop.hash else False
        if data[2] == "lsd":
            shop.lsd = True if not shop.lsd else False
        if data[2] == "grib":
            shop.grib = True if not shop.grib else False
        if data[2] == "food":
            shop.food = True if not shop.food else False
        shop.save()
        await shop_assorts(callback, edit=True)
    except Exception as e:
        print(e)
