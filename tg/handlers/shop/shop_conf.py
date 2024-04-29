from aiogram import Router, F, Bot
from asgiref.sync import sync_to_async
from ...models import Shop, TelegramUser
from ... import text
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, CommandObject
from ...states import ShopConfigurationsState
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
router = Router()


@router.callback_query(F.data == "shop_conf")
async def shop_config(callback_query: CallbackQuery, bot: Bot):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback_query.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="✍️ Название", callback_data=f"shopedit_title_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Описание", callback_data=f"shopedit_description_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Оператор", callback_data=f"shopedit_operator_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Саппорт", callback_data=f"shopedit_support_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Bot", callback_data=f"shopedit_bot_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Фото", callback_data=f"shopedit_photo_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Канал", callback_data=f"shopedit_channel_{shop.id}"))
            builder.add(InlineKeyboardButton(text="✍️ Чат", callback_data=f"shopedit_chat_{shop.id}"))
            builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
            builder.adjust(2, 2, 2, 2, 1)
            await callback_query.message.delete()
            await callback_query.message.answer(text.shop_conf_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)


@router.callback_query(F.data.startswith("shopedit_"))
async def shop_edit_owner(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split("_")
    if data[1] == "title":
        text = "⚙ Для изменения названия, введите команду\n`/editshoptitle` Новое название"
        await callback_query.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    elif data[1] == "description":
        text = "✍️ Введите новое описание"
        await callback_query.message.answer(text)
        await state.set_state(ShopConfigurationsState.awaiting_description)
    elif data[1] == "operator":
        text = ("⚙ Для изменения оператора, введите команду\n`/editshopoperator` Новая ссылка на профиль\n\n"
                "❕ ВАЖНО! Ссылка должна быть в образе https\n_Например https://t.me/telegram_")
        await callback_query.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    elif data[1] == "support":
        text = ("⚙ Для изменения саппорта, введите команду\n`/editshopsupport` Новая ссылка на профиль\n\n"
                "❕ ВАЖНО! Ссылка должна быть в образе https\n_Например https://t.me/telegram_")
        await callback_query.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    elif data[1] == "bot":
        text = ("⚙ Для изменения бота, введите команду\n`/editshopbot` Новая ссылка на бот\n\n"
                "❕ ВАЖНО! Ссылка должна быть в образе https\n_Например https://t.me/telegram_")
        await callback_query.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    elif data[1] == "photo":
        text = "🗾 Отправьте новое фото вашего магазина"
        await state.set_state(ShopConfigurationsState.awaiting_photo)
        await callback_query.message.answer(text)
    elif data[1] == "channel":
        text = ("⚙ Для изменения адреса канала, введите команду\n`/editshopchannel` _Новая ссылка на канал_")
        await callback_query.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    elif data[1] == "chat":
        text = ("⚙ Для изменения адреса чата, введите команду\n/editshopchat _Новая ссылка на чат_")
        await callback_query.message.answer(text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("editshoptitle"))
async def edit_shop_title(msg: Message, bot: Bot, command: CommandObject):
    data = command.args
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            shop.title = data
            shop.save(update_fields=['title'])
            await msg.answer(f"🛎 Успешно!\nНовое название {data}")
        except Exception as e:
                print(e)


@router.message(ShopConfigurationsState.awaiting_description)
async def shop_edit_description(msg: Message, state: FSMContext):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            shop.description = msg.text
            shop.save(update_fields=['description'])
            await msg.answer(f"🛎 Успешно!\nНовое описание сохранено↩\n\n{msg.text}")
            await state.clear()
        except Exception as e:
                print(e)


@router.message(Command("editshopoperator"))
async def edit_shop_operator(msg: Message, bot: Bot, command: CommandObject):
    data = command.args
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        if data.lower().startswith("https:"):
            try:
                shop = await sync_to_async(Shop.objects.get)(owner=user)
                shop.operator = data
                shop.save(update_fields=['operator'])
                await msg.answer(f"🛎 Успешно!\nНовый оператор {data}")
            except Exception as e:
                    print(e)


@router.message(Command("editshopsupport"))
async def edit_shop_support(msg: Message, bot: Bot, command: CommandObject):
    data = command.args
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        if data.lower().startswith("https:"):
            try:
                shop = await sync_to_async(Shop.objects.get)(owner=user)
                shop.support = data
                shop.save(update_fields=['support'])
                await msg.answer(f"🛎 Успешно!\nНовый саппорт {data}")
            except Exception as e:
                    print(e)


@router.message(Command("editshopbot"))
async def edit_shop_bot(msg: Message, bot: Bot, command: CommandObject):
    data = command.args
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        if data.lower().startswith("https:"):
            try:
                shop = await sync_to_async(Shop.objects.get)(owner=user)
                shop.bot = data
                shop.save(update_fields=['bot'])
                await msg.answer(f"🛎 Успешно!\nНовый адрес бота {data}")
            except Exception as e:
                    print(e)


@router.message(Command("editshopchannel"))
async def edit_shop_channel(msg: Message, bot: Bot, command: CommandObject):
    data = command.args
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        if data.lower().startswith("https:"):
            try:
                shop = await sync_to_async(Shop.objects.get)(owner=user)
                shop.channel = data
                shop.save(update_fields=['channel'])
                await msg.answer(f"🛎 Успешно!\nНовый адрес канала {data}")
            except Exception as e:
                    print(e)


@router.message(ShopConfigurationsState.awaiting_photo)
async def shop_edit_photo(msg: Message, state: FSMContext):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
            if msg.photo:
                photo_id = msg.photo[0].file_id
                shop.photo = photo_id
                shop.save(update_fields=['photo'])
                await msg.answer(f"🛎 Успешно!\nНовое фото сохранено↩\n\n{msg.text}")
                await state.clear()
        except Exception as e:
                print(e)


@router.message(Command("editshopchat"))
async def edit_shop_chat(msg: Message, bot: Bot, command: CommandObject):
    data = command.args
    user = await sync_to_async(TelegramUser.objects.get)(user_id=msg.from_user.id)
    if user.is_shop:
        if data.lower().startswith("https:"):
            try:
                shop = await sync_to_async(Shop.objects.get)(owner=user)
                shop.chat = data
                shop.save(update_fields=['chat'])
                await msg.answer(f"🛎 Успешно!\nНовый адрес чата {data}")
            except Exception as e:
                    print(e)