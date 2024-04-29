from aiogram import Router, F
from asgiref.sync import sync_to_async
from ... import text
from ...models import Shop, TelegramUser, AnnounceText
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from ...states import AnnounceTextState
router = Router()


@router.callback_query(F.data == "shop_announce")
async def shop_announce(callback_query: CallbackQuery):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback_query.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            if not announces:
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            builder = InlineKeyboardBuilder()
            for num, i in enumerate(announces):
                builder.add(InlineKeyboardButton(text=f"{await button_texter(num+1)} Анонс {'🟢' if i.on else '⚫'}", callback_data=f"change_announce_{i.id}"))
            builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
            builder.adjust(1)
            await callback_query.message.delete()
            await callback_query.message.answer(text=text.shop_announce_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)


async def button_texter(num):
    if num == 1:
        return '1⃣'
    elif num == 2:
        return '2⃣'
    elif num == 3:
        return '3⃣'
    return None


@router.callback_query(F.data.startswith("change_announce_"))
async def change_announce(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = callback.data.split("_")
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            announce = await sync_to_async(AnnounceText.objects.get)(id=data[2])
            if announce.shop == shop:
                await callback.message.delete()
                if announce.message_id and announce.from_chat_id:
                    builder = InlineKeyboardBuilder()
                    if not announce.on:
                        builder.add(InlineKeyboardButton(text="Включить 🟢", callback_data=f"announce_seton_{announce.id}"))
                    if announce.on:
                        builder.add(InlineKeyboardButton(text="Выключить 🔴", callback_data=f"announce_setoff_{announce.id}"))
                    builder.add(InlineKeyboardButton(text=f"{'Включить кнопки 🟢' if not announce.button else 'Выключить кнопки 🔴'}",
                                                     callback_data=f"announce_button_{announce.id}"))
                    builder.add(
                        InlineKeyboardButton(text="✍️  Редактировать", callback_data=f"announce_edit_{announce.id}"))
                    builder.add(InlineKeyboardButton(text="↩ Назад", callback_data="back_to_announces"))
                    builder.adjust(1)
                    if announce.button:
                        await bot.copy_message(chat_id=callback.message.chat.id, from_chat_id=announce.from_chat_id,
                                               message_id=announce.message_id, reply_markup=builder.as_markup())
                    if not announce.button:
                        await bot.forward_message(chat_id=callback.message.chat.id, from_chat_id=announce.from_chat_id, message_id=announce.message_id)
                        await callback.message.answer("🗣 *Анонс панель*\n\n_Выберите опцию_:", reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await state.set_state(AnnounceTextState.awaiting_announce)
                    await state.update_data(announce_id=announce.id)
                    await callback.message.answer("🔘 Пожалуйста перешлите ваше анонс-сообщение")

        except Exception as e:
            print(e)


@router.message(AnnounceTextState.awaiting_announce)
async def awaiting_announce_state(msg: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    print(data)
    announce_id = data.get("announce_id")
    print(announce_id)
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    announce = await sync_to_async(AnnounceText.objects.get)(id=announce_id)
    if user.is_shop or user.is_admin:
        try:
            shop = await sync_to_async(Shop.objects.get)(id=announce.shop.id)
            if announce.shop == shop:
                announce.from_chat_id = msg.chat.id
                announce.message_id = msg.message_id
                announce.save(update_fields=["from_chat_id", "message_id"])
                builder = InlineKeyboardBuilder()
                back_builder = InlineKeyboardBuilder()
                back_builder.add(InlineKeyboardButton(text="↩ Назад", callback_data="back_to_announces"))
                if announce.button:
                    shop = announce.shop
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
                    await bot.copy_message(chat_id=msg.chat.id, from_chat_id=announce.from_chat_id, message_id=announce.message_id, reply_markup=builder.as_markup())
                    await msg.answer("📍 Анонс успешно добавлен, вы сможете включить/выключить его в разделе анонсов\n\n"
                                     "_Рекомендуем вам включить кнопки, это увеличит колличество откликов_",
                                     parse_mode=ParseMode.MARKDOWN, reply_markup=back_builder.as_markup())
                    await state.clear()
                    return
                elif not announce.button:
                    await bot.forward_message(chat_id=msg.chat.id, from_chat_id=announce.from_chat_id, message_id=announce.message_id)
                    await msg.answer("📍 Анонс успешно добавлен, вы сможете включить/выключить его в разделе анонсов\n\n"
                                     "_Рекомендуем вам включить кнопки, это увеличит колличество откликов_",
                                     parse_mode=ParseMode.MARKDOWN, reply_markup=back_builder.as_markup())
        except Exception as e:
            print(e)


@router.callback_query(F.data.startswith("announce_"))
async def announce_editor(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = callback.data.split("_")
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
    announce = await sync_to_async(AnnounceText.objects.get)(id=data[2])
    if user == announce.shop.owner or user.is_admin:
        if data[1] == "seton":
            announce.on = True
            announce.save(update_fields=['on'])
            await in_announce_for_edit(callback, announce, bot)
        if data[1] == "setoff":
            announce.on = False
            announce.save(update_fields=['on'])
            await in_announce_for_edit(callback, announce, bot)
        if data[1] == "edit":
            await state.set_state(AnnounceTextState.awaiting_announce)
            await state.update_data(announce_id=announce.id)
            await callback.message.answer("🔘 Пожалуйста перешлите ваше анонс-сообщение")
        if data[1] == "button":
            if announce.button:
                announce.button = False
                announce.save(update_fields=['button'])
                await in_announce_for_edit(callback, announce, bot)
            elif not announce.button:
                announce.button = True
                announce.save(update_fields=['button'])
                await in_announce_for_edit(callback, announce, bot)


async def in_announce_for_edit(callback, announce, bot):
    builder = InlineKeyboardBuilder()
    if not announce.on:
        builder.add(InlineKeyboardButton(text="Включить 🟢", callback_data=f"announce_seton_{announce.id}"))
    if announce.on:
        builder.add(InlineKeyboardButton(text="Выключить 🔴", callback_data=f"announce_setoff_{announce.id}"))
    builder.add(InlineKeyboardButton(text=f"{'Включить кнопки 🟢' if not announce.button else 'Выключить кнопки 🔴'}",
                                     callback_data=f"announce_button_{announce.id}"))
    builder.add(InlineKeyboardButton(text="✍️  Редактировать", callback_data=f"announce_edit_{announce.id}"))
    builder.add(InlineKeyboardButton(text="↩ Назад", callback_data="back_to_announces"))
    builder.adjust(1)

    await callback.message.edit_text("🗣 *Анонс панель*\n\n_Выберите опцию_:",
                                     reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data == "back_to_announces")
async def back_to_announces(callback: CallbackQuery, bot: Bot):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            if not announces:
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                await sync_to_async(AnnounceText.objects.create)(shop=shop)
                announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
            builder = InlineKeyboardBuilder()
            for num, i in enumerate(announces):
                builder.add(InlineKeyboardButton(text=f"{await button_texter(num + 1)} Анонс {'🟢' if i.on else '⚫'}",
                                                 callback_data=f"change_announce_{i.id}"))
            builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
            builder.adjust(1)


            await callback.message.edit_text(text=text.shop_announce_text, reply_markup=builder.as_markup(),
                                                parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)
