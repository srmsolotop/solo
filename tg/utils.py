from .models import Shop, AnnounceText, Chat
from asgiref.sync import sync_to_async
import asyncio
from aiogram import Bot
from aiogram.utils.keyboard import  InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


async def shop_texter(shop):
    text = ""
    text += shop.title + "\n\n"
    text += shop.description + "\n\n"
    return text


async def send_periodic_message(bot: Bot):
    while True:
        print("IN PERIODIC CHECK")
        chats = await sync_to_async(Chat.objects.all)()
        for chat in chats:
            shops = await sync_to_async(Shop.objects.filter)(main_chat=chat, paused=False)
            for shop in shops:
                announces = await sync_to_async(AnnounceText.objects.filter)(shop=shop)
                for announce in announces:
                    if announce.on:
                        if announce.from_chat_id and announce.message_id:
                            if announce.button:
                                builder = InlineKeyboardBuilder()
                                bot_info = await bot.get_me()
                                builder.add(InlineKeyboardButton(text=f"{shop.title}",
                                                                  url=f"https://t.me/{bot_info.username}?start=getshop_{shop.id}"))
                                await bot.copy_message(chat_id=chat.chat_id, from_chat_id=announce.from_chat_id, message_id=announce.message_id, reply_markup=builder.as_markup())
                                await asyncio.sleep(3000)
                            elif not announce.button:
                                await bot.forward_message(chat_id=chat.chat_id, from_chat_id=announce.from_chat_id, message_id=announce.message_id)
                                await asyncio.sleep(3000)
        await asyncio.sleep(60)
