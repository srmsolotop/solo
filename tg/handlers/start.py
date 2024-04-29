from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from ..models import TelegramUser, Trigger, Shop, ShopReview, Rating, Chat, Exchange
from .. import kb
from .. import text as tx
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..states import TriggerState, AddShopState
from ..utils import shop_texter
from .shop.rater import rater, get_shop_rating_text
from django.utils import timezone
from datetime import datetime, timedelta
router = Router()


# @router.message()
# async def photo_adder(msg: Message):
#     print("CHAT_ID", msg.chat.id)
#     if msg.photo:
#         photo_id = msg.photo[0].file_id
#         print(photo_id)


@router.message(Command("start"))
async def start_command(msg: Message, state: FSMContext, bot: Bot, command: CommandObject):
    user, created = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=msg.from_user.id)
    user.first_name = msg.from_user.first_name
    user.last_name = msg.from_user.last_name
    user.username = msg.from_user.username
    user.save()
    args = command.args
    if args:
        data = args.split("_")
        if data[0] == "newshop":
            try:
                shop = await sync_to_async(Shop.objects.get)(id=data[1])
                if not shop.owner:
                    shop.owner = user
                    if not shop.description and not shop.photo:
                        await msg.answer(f"Приветствую вас {shop.title}\n\n"
                                         f"Отправьте красиво оформленное описание с вашими прайсами\n"
                                         f"\n\nС уважением, Администрация SRM")
                        user.is_shop = True
                        user.save()
                        shop.save()
                        await state.set_state(AddShopState.awaiting_description)
                        await state.update_data(shop_id=shop.id)
                    else:
                        await msg.answer(f"Ваш панель магазина {shop.title}", reply_markup=kb.shop_panel)
            except Exception as e:
                print(e)
            return
        elif data[0] == "getshop":
            try:
                shop = await sync_to_async(Shop.objects.get)(id=data[1])
                builder = InlineKeyboardBuilder()
                if shop.bot:
                    builder.add(InlineKeyboardButton(text="BOT", url=shop.bot))
                if shop.operator:
                    builder.add(InlineKeyboardButton(text="OPERATOR", url=shop.operator))
                if shop.support:
                    builder.add(InlineKeyboardButton(text="SUPPORT", url=shop.support))
                if shop.channel:
                    builder.add(InlineKeyboardButton(text="CHANNEL", url=shop.channel))
                if shop.chat:
                    builder.add(InlineKeyboardButton(text="CHAT", url=shop.chat))
                text = await shop_texter(shop)
                builder.adjust(1)
                today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)
                existing_reviews_today = await sync_to_async(ShopReview.objects.filter)(user=user, shop=shop,
                                                                                        created_at__gte=today_start,
                                                                                        created_at__lt=today_end)
                existing_reviews_today = existing_reviews_today.count()

                if existing_reviews_today == 0:
                    await sync_to_async(ShopReview.objects.create)(user=user, shop=shop)
                    reviews = await sync_to_async(ShopReview.objects.filter)(shop=shop)
                    shop.reviews = len(reviews)
                    shop.save()

                try:
                    if shop.photo:
                        await bot.send_photo(chat_id=msg.from_user.id, photo=shop.photo, caption=text,
                                             reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
                    else:
                        await msg.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
                    await rater(user, shop, msg)
                    return
                except Exception as e:
                    if shop.photo:
                        await bot.send_photo(chat_id=msg.from_user.id, photo=shop.photo, caption=text,
                                             reply_markup=builder.as_markup())
                    else:
                        await msg.answer(text, reply_markup=builder.as_markup())
                    await rater(user, shop, msg)
                    return

            except Exception as e:
                print(e)
        elif data[0] == "getexchange":
            exchanges = await sync_to_async(Exchange.objects.all)()
            builder = InlineKeyboardBuilder()
            for i in exchanges:
                builder.add(InlineKeyboardButton(text=f"{i.username}", url=f"{i.link}"))
            builder.adjust(1)
            await msg.answer("Актуальные обемнники", reply_markup=builder.as_markup())
            return



    if user.is_admin:
        shops = await sync_to_async(Shop.objects.all)()
        text = "".join(f"🆔 ➖ {i.id} {i.title}\n" for i in shops)
        await msg.answer(f"🎟 Админ панель\n\n{text}", reply_markup=kb.admin_panel)
        return
    if user.is_shop:
        await msg.answer(tx.shop_panel_text, reply_markup=kb.shop_panel, parse_mode=ParseMode.MARKDOWN)
        return
    else:
        await menu(msg, bot)


@router.message(lambda message: message.text and message.text.lower() in ["меню", "гаш", "шишки", "грибы", "лсд", "lsd", "каннафуд"])
async def menu(msg: Message, bot: Bot):
    user, created = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=msg.from_user.id)
    user.first_name = msg.from_user.first_name
    user.last_name = msg.from_user.last_name
    user.username = msg.from_user.username
    user.save()
    photo_id = "AgACAgIAAxkBAAIETmYg0VOFdESvdhpUbJF9BSqnH4JfAALu6DEbMgwJSUx0KzArKaqIAQADAgADcwADNAQ"

    shops = await sync_to_async(Shop.objects.filter)(paused=False)

    if msg.text.lower() == "гаш":
        shops = await sync_to_async(Shop.objects.filter)(hash=True, paused=False)
    elif msg.text.lower() == "шишки":
        shops = await sync_to_async(Shop.objects.filter)(shish=True, paused=False)
    elif msg.text.lower() == "грибы":
        shops = await sync_to_async(Shop.objects.filter)(grib=True, paused=False)
    elif msg.text.lower() == "lsd" or msg.text.lower() == "лсд":
        shops = await sync_to_async(Shop.objects.filter)(lsd=True, paused=False)
    elif msg.text.lower() == "каннафуд":
        shops = await sync_to_async(Shop.objects.filter)(food=True, paused=False)
    keyboard = InlineKeyboardBuilder()
    text = "🐪Silk Road Marketplace🐪\n         💃Presents🕺\n\n"
    for i in shops:
        rating, stars = await get_shop_rating_text(i)
        text +=f"*{i.title}*" + f' *{rating if rating else ""}*{""+stars if stars else ""}\n'
        if i.hash:
            text += "➖➖🍫 *Гашиш*➖➖\n"
        if i.shish:
            text += "➖➖🌳 *Шишки*➖➖\n"
        if i.lsd:
            text += "➖➖👅 *LSD*➖➖\n"
        if i.grib:
            text += "➖➖🍄 *Грибы*➖➖\n"
        if i.food:
            text += "➖➖🍩 *Каннаfood*➖➖\n"
        text += f"\n"
        bot_info = await bot.get_me()
        keyboard.add(InlineKeyboardButton(text=f"{i.title}", url=f"https://t.me/{bot_info.username}?start=getshop_{i.id}"))
    keyboard.add(InlineKeyboardButton(text="Обменка", url=f"https://t.me/{bot_info.username}?start=getexchange_ex"))
    keyboard.adjust(1)
    try:
        await bot.send_photo(chat_id=msg.chat.id, photo=photo_id, caption=text,
                             reply_markup=keyboard.as_markup(), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(e)
        await msg.answer(text, reply_markup=keyboard.as_markup(), parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data == "back")
async def back_to_main(callback_query: CallbackQuery):
    user, created = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=callback_query.from_user.id)
    user.first_name = callback_query.from_user.first_name
    user.last_name = callback_query.from_user.last_name
    user.username = callback_query.from_user.username
    user.save()
    await callback_query.message.delete()
    if user.is_admin:
        shops = await sync_to_async(Shop.objects.all)()
        text = "".join(f"🆔 ➖ {i.id} {i.title}\n" for i in shops)
        await callback_query.message.answer(f"🎟 Админ панель\n\n{text}", reply_markup=kb.admin_panel)
    if user.is_shop:
        await callback_query.message.answer(tx.shop_panel_text, reply_markup=kb.shop_panel, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("send_invite_to_chat"))
async def superadmin_sender(msg: Message, bot: Bot):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_super_admin:
        chat = await sync_to_async(Chat.objects.first)()
        try:
            text = tx.inviter_text
            text += f"[ССЫЛКА В ЧАТ]({chat.link})\n"
            bot_info = await bot.get_me()
            text += f"[БОТ](https://t.me/{bot_info.username}?)\n"
            text += f"[КАНАЛ]({chat.channel_link})"
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="CHAT", url=f"{chat.link}"))
            builder.add(InlineKeyboardButton(text="BOT", url=f"https://t.me/{bot_info.username}?start="))
            builder.add(InlineKeyboardButton(text="CHANNEL", url=f"{chat.channel_link}"))
            await bot.send_photo(chat_id=chat.chat_id, photo=chat.photo, caption=text,
                                 reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)
            print(e)