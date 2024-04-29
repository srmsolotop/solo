import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import io
from aiogram import Router, F, Bot
from asgiref.sync import sync_to_async
from ...models import Shop, ShopReview, TelegramUser
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
router = Router()
from datetime import datetime, timedelta
from django.utils import timezone
from aiogram.enums.parse_mode import ParseMode
import re


async def shop_statistics_generator():
    shops = await sync_to_async(Shop.objects.all)()
    titles = [re.sub(r'[^\w\s]', '', shop.title) for shop in shops]
    data = {
        'Название': titles,
        'Отклики': [shop.reviews for shop in shops],
    }
    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Отклики', y='Название', data=df, palette='viridis', width=0.5, hue='Название', dodge=False, legend=False)
    # sns.barplot(x='Отклики', y='Название', data=df, orient='h', width=0.5, dodge=False)

    plt.xlabel('Количество откликов', fontsize=14)
    plt.ylabel('SHOPS', fontsize=14)
    plt.title('Отклики в магазинах', fontsize=16)
    plt.grid(True)

    for index, value in enumerate(df['Отклики']):
        plt.text(value, index, str(value))
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.family'] = "Playfair Display"

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer


async def date_time_stats(shop, days):
    today = timezone.now()
    days_ago = today - timedelta(days=days)
    result = ShopReview.objects.filter(shop=shop, created_at__gte=days_ago, created_at__lte=today)
    return result


@router.callback_query(F.data == "shop_statistics")
async def shop_statistics(callback_query: CallbackQuery, bot: Bot):
    await callback_query.message.delete()
    user = await sync_to_async(TelegramUser.objects.get)(user_id=callback_query.from_user.id)
    if user.is_shop:
        buffer = await shop_statistics_generator()
        input_file = types.BufferedInputFile(buffer.getvalue(), filename="chart.png")
        try:
            shop = await sync_to_async(Shop.objects.get)(owner=user)
        except Exception as e:
            print(e)

        text = f"    🐪Silk Road Statistics🐪\n💯 Предоставляем вам статистику переходов из SRM\n\n〽{shop.title}〽\n\n"
        text += f"🌠 *За всё время* ⏬\n➖`{shop.reviews}` _переходов_\n\n"
        text += f"🎆 *За 30 дней* ⏬\n➖ `{len(await date_time_stats(shop, 30))}` _переходов_\n\n"
        text += f"🎇 *За 7 дней* ⏬\n➖ `{len(await date_time_stats(shop, 7))}` _переходов_\n\n"
        text += f"☀ *За сегодня* ⏬\n➖ `{len(await date_time_stats(shop, 1))}` _переходов_\n\n"

        text += (f"_- Ниже вы можете запросить имена пользователей, статистика защищена от накрутки, "
                 f"показывает реальный интерес к вашему магазину. Что бы его увеличить настройте анонс в боте_.")

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🎆 За 30 дней", callback_data=f"shopstats_30_{shop.id}"))
        builder.add(InlineKeyboardButton(text="🎇 За 7 дней", callback_data=f"shopstats_7_{shop.id}"))
        builder.add(InlineKeyboardButton(text="☀ За сегодня", callback_data=f"shopstats_1_{shop.id}"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back"))
        builder.adjust(1)

        await bot.send_photo(callback_query.from_user.id, photo=input_file, caption=text, reply_markup=builder.as_markup(),
                             parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data.startswith("shopstats"))
async def show_users_stats(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    days = int(data[1])
    shop_id = data[2]

    try:
        shop = await sync_to_async(Shop.objects.get)(id=shop_id)
        user = await sync_to_async(TelegramUser.objects.get)(user_id=callback_query.from_user.id)
        if shop.owner == user:
            reviews = await date_time_stats(shop, days)
            if reviews:
                text = f'📍 Пользователи перешедшие к вам за {str(days) + " дней" if days > 1 else "сегодня"} \n\n'
                for num, i in enumerate(reviews):
                    text += f'{num+1}. {"@"+i.user.username if i.user.username else i.user.user_id}\n'
                await callback_query.message.answer(text)
            else:
                await callback_query.message.answer("💡 У вас нет переходов за данный период, проявляйте больше активности в чате")
    except Exception as e:
        print(e)

