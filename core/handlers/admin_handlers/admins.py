from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from core.filters.filters import IsDirectAdminMessage, IsDirectAdminCallback
from core.states.admin_states import (
    FindPlayer,
    ChangeSkillPoints,
    ChangeBalance,
    WaitForNextState,
)
from core.keyboards.inline import admin_menu, return_to_admin_menu
from core.utils.player_utils import player_settings, skill_level_calculator
from core.db.models import Player


admin_commands_router = Router()


# getting to admin menu with command
@admin_commands_router.message(IsDirectAdminMessage(), Command("admin"))
async def open_admin_menu_m(message: types.Message, state: FSMContext = None):
    if state is not None:
        await state.clear()
    await message.answer(text="Choose one of the options:", reply_markup=admin_menu)


# getting to admin menu with callback
@admin_commands_router.callback_query(
    IsDirectAdminCallback(),
    F.data == "admin_menu",
)
async def open_admin_menu_c(query: types.CallbackQuery, state: FSMContext = None):
    if state is not None:
        await state.clear()
    await query.bot.edit_message_text(
        "Choose one of the options:",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=admin_menu,
    )
    await query.answer()


# searching player by id (setting fsm)
@admin_commands_router.callback_query(
    IsDirectAdminCallback(),
    F.data == "search_player_by_id",
)
async def get_player_id(query: types.CallbackQuery, state: FSMContext):
    await query.bot.edit_message_text(
        "Type id of the player you want to find",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=return_to_admin_menu,
    )
    await state.set_state(FindPlayer.GET_PLAYER_ID)
    await query.answer()


# getting player id to search player
@admin_commands_router.message(
    FindPlayer.GET_PLAYER_ID, IsDirectAdminMessage(), F.text.regexp(r"\d{1,20}")
)
async def find_player(message: types.Message, state: FSMContext):
    player = Player.select().where(Player.player_telegram_id == message.text)
    if player.exists():
        await state.clear()
        player = player.get()
        characteristics, player_settings_buttons = player_settings(player)
        last_settings_message = await message.bot.send_message(
            chat_id=message.chat.id,
            text=characteristics,
            reply_markup=player_settings_buttons,
        )
        await state.update_data(last_settings_message=last_settings_message)
        await state.set_state(WaitForNextState.WAIT_FOR_NEXT_STATE)
    else:
        await message.answer("No user was found with such id")


# banning player
@admin_commands_router.callback_query(
    IsDirectAdminCallback(), F.data.startswith("ban_player_")
)
async def ban_player(query: types.CallbackQuery):
    player_id = query.data.split("_")[-1]
    player = Player.select().where(Player.player_telegram_id == player_id).get()
    player.player_ban = True
    player.save()
    characteristics, player_settings_buttons = player_settings(player)
    await query.bot.edit_message_text(
        characteristics,
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=player_settings_buttons,
    )
    await query.answer("🔴 Player is banned")


# unbanning player
@admin_commands_router.callback_query(
    IsDirectAdminCallback(), F.data.startswith("unban_player_")
)
async def unban_player(query: types.CallbackQuery):
    player_id = query.data.split("_")[-1]
    player = Player.select().where(Player.player_telegram_id == player_id).get()
    player.player_ban = False
    player.save()
    characteristics, player_settings_buttons = player_settings(player)
    await query.bot.edit_message_text(
        characteristics,
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=player_settings_buttons,
    )
    await query.answer("🟢 Player is unbanned")


# changing player's skill points (setting fsm)
@admin_commands_router.callback_query(
    FindPlayer.WAIT_FOR_NEXT_STATE,
    IsDirectAdminCallback(),
    F.data.startswith("change_player_skill_points_"),
)
async def get_player_skill_points(query: types.CallbackQuery, state: FSMContext):
    player_id = query.data.split("_")[-1]
    await query.bot.edit_message_text(
        "Type the number of skill points you want to set for the player",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=return_to_admin_menu,
    )
    await state.update_data(player_id=player_id)
    await state.set_state(ChangeSkillPoints.GET_SKILL_POINTS)
    await query.answer()


# getting num of skill points to set to player
@admin_commands_router.message(
    ChangeSkillPoints.GET_SKILL_POINTS,
    IsDirectAdminMessage(),
    F.text.regexp(r"\b[-+]?\d+$"),
)
async def change_player_skill_points(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_settings_message = info["last_settings_message"]
    player = Player.select().where(Player.player_telegram_id == info["player_id"]).get()
    skill_points = int(message.text)
    level, points_to_next_level = skill_level_calculator(skill_points=skill_points)
    (
        player.player_skill_points,
        player.player_skill_points_to_next_level,
        player.player_skill_level,
    ) = (skill_points, points_to_next_level, level)
    player.save()
    player_characteristics, player_buttons = player_settings(player=player)
    await message.bot.delete_message(
        chat_id=message.chat.id, message_id=last_settings_message.message_id
    )
    last_settings_message = await message.bot.send_message(
        chat_id=message.chat.id,
        text=player_characteristics,
        reply_markup=player_buttons,
    )
    await state.update_data(last_settings_message=last_settings_message)
    await state.set_state(WaitForNextState.WAIT_FOR_NEXT_STATE)


# changing player's balance
@admin_commands_router.callback_query(
    WaitForNextState.WAIT_FOR_NEXT_STATE,
    IsDirectAdminCallback(),
    F.data.startswith("change_player_balance_"),
)
async def get_player_balance(query: types.CallbackQuery, state: FSMContext):
    player_id = query.data.split("_")[-1]
    await query.bot.edit_message_text(
        "Type the new balance you want to set for the player",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=return_to_admin_menu,
    )
    await state.update_data(player_id=player_id)
    await state.set_state(ChangeBalance.GET_NEW_BALANCE)
    await query.answer()


# getting num of balance to set to player
@admin_commands_router.message(
    ChangeBalance.GET_NEW_BALANCE, IsDirectAdminMessage(), F.text.regexp(r"\b[-+]?\d+$")
)
async def change_player_balance(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_settings_message = info["last_settings_message"]
    player = Player.select().where(Player.player_telegram_id == info["player_id"]).get()
    balance = int(message.text)
    player.player_balance = balance
    player.save()
    player_characteristics, player_buttons = player_settings(player=player)
    await message.bot.delete_message(
        chat_id=message.chat.id, message_id=last_settings_message.message_id
    )
    last_settings_message = await message.bot.send_message(
        chat_id=message.chat.id,
        text=player_characteristics,
        reply_markup=player_buttons,
    )
    await state.update_data(last_settings_message=last_settings_message)
    await state.set_state(ChangeBalance.WAIT_FOR_NEXT_STATE)