from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from core.utils.player_utils import (
    update_player_information,
    create_new_player,
    get_player_characteristics,
)
from core.keyboards.inline import main_menu, main_menu_for_admin, get_to_main_menu
from core.filters.filters import check_for_admin, IsDirectStart, IsDirectCallback
from core.db.models import Player


user_commands_router = Router()


# start handler
@user_commands_router.message(IsDirectStart(), Command("start"))
async def start_command(message: types.Message, state: FSMContext = None):
    await state.clear()
    mm = main_menu
    player = Player.select().where(Player.player_telegram_id == message.from_user.id)
    if player.exists():
        update_player_information(player=player, message=message)
    else:
        create_new_player(player=Player, message=message)
    fullname = message.from_user.full_name
    await message.answer(
        f"Welcome to the world of quests <strong>{fullname}</strong>!. Here you can try your knowledge and luck!"
    )
    if check_for_admin(admin_id=message.from_user.id):
        mm = main_menu_for_admin
    await message.answer("Choose one of the menu options:", reply_markup=mm)


# showing player's characteristics
@user_commands_router.callback_query(
    IsDirectCallback(), F.data == "show_characteristics"
)
async def show_player_characteristics(query: types.CallbackQuery):
    player = Player.select().where(Player.player_telegram_id == query.from_user.id)
    if player.exists():
        player = player.get()
        player_characteristics = get_player_characteristics(player=player)
        await query.bot.edit_message_text(
            text=player_characteristics,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=get_to_main_menu,
        )
        await query.answer()
    else:
        await query.answer(
            "Please type /start and try again"
        )


# returning to main menu
@user_commands_router.callback_query(IsDirectCallback(), F.data == "get_to_main_menu")
async def return_to_main_menu(query: types.CallbackQuery, state: FSMContext = None):
    await state.clear()
    mm = main_menu
    if check_for_admin(admin_id=query.from_user.id):
        mm = main_menu_for_admin
    await query.bot.edit_message_text(
        "Choose one of the menu options:",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=mm,
    )
    await query.answer()
