import os
import django
from aiogram.client.default import DefaultBotProperties

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

import asyncio
import logging
from tg.utils import send_periodic_message


async def main():
    from aiogram.enums.parse_mode import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram import Bot, Dispatcher
    from tg.handlers import start
    from tg.handlers.shop import shop, shop_stats, rater, shop_conf, announces, shop_assorts
    from tg.handlers.admin import admin_shops, admin_edit_announce

    bot = Bot(token='7188725807:AAFIznEouLvd5uQGJwNJpyXTcnhxMH5qrCY', default=DefaultBotProperties(parse_mode=None))
    asyncio.create_task(send_periodic_message(bot))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start.router, shop.router, shop_stats.router, rater.router,
                       shop_conf.router, announces.router, admin_shops.router, shop_assorts.router, admin_edit_announce.router,
                       )
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
