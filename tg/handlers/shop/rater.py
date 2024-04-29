from aiogram import Router, F
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import timedelta
from ...models import Rating
from ...models import Shop, TelegramUser, ShopReview
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()


async def rater(user, shop, msg):
    today = timezone.now()
    days_30 = today - timedelta(days=30)
    reviews = ShopReview.objects.filter(shop=shop, user=user, created_at__gte=days_30, created_at__lte=today)
    days_7 = today - timedelta(days=7)
    rates = await sync_to_async(Rating.objects.filter)(user=user, shop=shop,
                                                       created_at__gte=days_7, created_at__lte=today)
    if len(reviews) >= 10 and not rates:
        keyboard = InlineKeyboardBuilder()
        for i in range(5, 0, -1):
            keyboard.add(InlineKeyboardButton(text="⭐"*i, callback_data=f"addrate_{i}_{shop.id}"))
        keyboard.adjust(1, 1, 3)
        await msg.answer(f"👣 Вы за последнее время часто посещали \n{shop.title}\n\n"
                         f"Рейтинг магазина показана всем участника площадки\nВаша оценка влияет на дальнейшие покупки остальных клиентов\n\n_Оцените магазин_",
                         reply_markup=keyboard.as_markup(), parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data.startswith("addrate_"))
async def addrate_to_shop(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback_query.from_user.id)
        rate = data[1]
        shop_id = data[2]
        shop = await sync_to_async(Shop.objects.get)(id=shop_id)
        rating = await sync_to_async(Rating.objects.create)(user=user, shop=shop, rate=rate)
        await callback_query.message.delete()
        await callback_query.message.answer("💟 Ваша оценка принята, спасибо что улучшаете качество работы площадки")
    except Exception as e:
        print(e)


async def get_shop_rating_text(shop):
    ratings = await sync_to_async(Rating.objects.filter)(shop=shop)
    ratings = ratings.values_list('rate', flat=True)
    total_rating = sum(ratings)
    result = total_rating / len(ratings) if total_rating > 0 else None
    if result:
        result = round(result, 1)
        if result > 4.7:
            return f"🌟 {result}/5", "  \[⭐.⭐.⭐.⭐.⭐]"
        elif result >= 4:
            return f"🌟 {result}/5", "      \[⭐.⭐.⭐.⭐]"
        elif result >= 3:
            return f"🌟 {result}/5", "          \[⭐.⭐.⭐]"
        elif result >= 2:
            return f"🌟 {result}/5", "             \[⭐.⭐]"
        elif result >= 1:
            return f"🌟 {result}/5", "               \[⭐]"
    else:
        return None, None
