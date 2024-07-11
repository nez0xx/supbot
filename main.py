import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from handlers import router
from settings import settings


TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
WEBHOOK_DOMAIN = settings.WEBHOOK_DOMAIN
WEBHOOK_PATH = settings.WEBHOOK_PATH
APP_HOST = settings.APP_HOST
APP_PORT = settings.APP_PORT


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)

    try:
        if not WEBHOOK_DOMAIN:
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types()
            )
        else:
            aiohttp_logger = logging.getLogger('aiohttp.access')
            aiohttp_logger.setLevel(logging.DEBUG)

            await bot.set_webhook(
                url=WEBHOOK_DOMAIN + WEBHOOK_PATH,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            app = web.Application()
            SimpleRequestHandler(dispatcher=dp,
                                 bot=bot).register(app, path=WEBHOOK_PATH)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=APP_HOST, port=APP_PORT)
            await site.start()

            await asyncio.Event().wait()
    except RuntimeError:
        pass
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
