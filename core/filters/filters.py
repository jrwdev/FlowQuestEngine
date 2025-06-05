from aiogram import types
from aiogram.filters import BaseFilter


from core.db.models import Admin, Player


def check_for_admin(admin_id):
    admin = Admin.select().where(Admin.admin_telegram_id == admin_id)
    if admin.exists():
        return True
    return False


class IsDirectStart(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        if message.chat.id == message.from_user.id:
            return True
        return False


class IsDirectMessage(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        if message.chat.id == message.from_user.id:
            player = (
                Player.select()
                .where(Player.player_telegram_id == message.from_user.id)
                .get()
            )
            if player.player_ban is False:
                return True
        return False


class IsDirectCallback(BaseFilter):
    async def __call__(self, query: types.CallbackQuery) -> bool:
        if query.message.chat.id == query.from_user.id:
            player = (
                Player.select()
                .where(Player.player_telegram_id == query.from_user.id)
                .get()
            )
            if player.player_ban is False:
                return True
        return False


class IsDirectAdminMessage(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        admin = Admin.select().where(Admin.admin_telegram_id == message.from_user.id)
        if admin.exists():
            if message.chat.id == message.from_user.id:
                return True
            return False
        return False


class IsDirectAdminCallback(BaseFilter):
    async def __call__(self, query: types.CallbackQuery) -> bool:
        admin = Admin.select().where(Admin.admin_telegram_id == query.from_user.id)
        if admin.exists():
            if query.message.chat.id == query.from_user.id:
                return True
            return False
        return False
