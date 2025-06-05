import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from core.settings import settings
from core.handlers.admin_handlers.admins import admin_commands_router
from core.handlers.admin_handlers.manage_achievements import (
    achievment_management_router,
)
from core.handlers.admin_handlers.manage_quests import quest_manage_commands_router
from core.handlers.user_handlers.users import user_commands_router
from core.handlers.user_handlers.quests import quest_interaction_commands_router


async def start_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Bot is turned <b>on</b>")


async def stop_bot(bot: Bot):
    await bot.send_messsage(settings.bots.admin_id, text="Bot is turned <b>off</b>")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    bot = Bot(token=settings.bots.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(
        admin_commands_router,
        achievment_management_router,
        quest_manage_commands_router,
        user_commands_router,
        quest_interaction_commands_router,
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
