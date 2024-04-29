from aiogram import Router, Bot, F
from asgiref.sync import sync_to_async
from ...states import AddShopState
from ...models import Shop, TelegramUser
from ...utils import shop_texter
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
router = Router()


@router.callback_query(F.data == 'add_shop')
async def add_shop_func(callback_query: CallbackQuery, state: FSMContext):
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback_query.from_user.id)
    if user.is_admin:
        await callback_query.message.answer("Введите название шопа, желательно оберните в смайлики, дайте красивый вид названию")
        await state.set_state(AddShopState.awaiting_tittle)


@router.message(AddShopState.awaiting_tittle)
async def addshop_tittle_state(msg: Message, state: FSMContext, bot: Bot):
    new_shop = await sync_to_async(Shop.objects.create)(title=msg.text)
    bot_info = await bot.get_me()
    await msg.answer(f"Отправьте эту ссылку вашему новому шопу для конфигурации настроек "
                     f"`https://t.me/{bot_info.username}?start=newshop_{new_shop.id}`", parse_mode=ParseMode.MARKDOWN)
    await state.clear()


@router.message(AddShopState.awaiting_description)
async def add_desc_shop_state(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    shop_id = data.get("shop_id")
    shop = await sync_to_async(Shop.objects.get)(id=shop_id)
    shop.description = msg.text
    shop.save(update_fields=['description'])
    await msg.answer("Отлично, описание есть!\nТеперь отправьте фотографию шопа")
    await state.set_state(AddShopState.awaiting_photo)


@router.message(AddShopState.awaiting_photo)
async def add_photo_shop_state(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    shop_id = data.get("shop_id")
    shop = await sync_to_async(Shop.objects.get)(id=shop_id)
    if msg.photo:
        photo_id = msg.photo[0].file_id
        shop.photo = photo_id
        shop.save()
        text = await shop_texter(shop)
        await bot.send_photo(chat_id=msg.from_user.id, photo=shop.photo, caption=text)
        await state.clear()