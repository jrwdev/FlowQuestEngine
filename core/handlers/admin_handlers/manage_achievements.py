from aiogram import types, F, Router
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


from core.filters.filters import IsDirectAdminCallback, IsDirectAdminMessage
from core.keyboards.inline import achievement_menu_settings, return_to_achievement_menu
from core.states.achievement_states import CreateAchievemnt, ChangeAchievementName
from core.utils.quest_utils import achievement_info
from core.db.models import Achievement, MainQuest


achievment_management_router = Router()


# open achievement menu
@achievment_management_router.callback_query(
    IsDirectAdminCallback(), F.data == "achievement_menu"
)
async def achievement_menu(query: types.CallbackQuery, state: FSMContext = None):
    if state is not None:
        await state.clear()
    await query.bot.edit_message_text(
        "Choose one of the options",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=achievement_menu_settings,
    )
    await query.answer()


# creating achievement
@achievment_management_router.callback_query(
    IsDirectAdminCallback(), F.data == "create_achievement"
)
async def create_achievement(query: types.CallbackQuery, state: FSMContext):
    await query.bot.edit_message_text(
        "Type the name of the new achievement",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=return_to_achievement_menu,
    )
    await state.set_state(CreateAchievemnt.GET_ACHIEVEMENT_NAME)
    await state.update_data(last_query=query)
    await query.answer()


# get the name of the achievement and set it
@achievment_management_router.message(
    CreateAchievemnt.GET_ACHIEVEMENT_NAME, IsDirectAdminMessage(), F.text.regexp(r".+")
)
async def get_achievement_name(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("100 symbols limit")
        return 0
    state_data = await state.get_data()
    last_query = state_data["last_query"]
    await state.update_data(achievement_name=message.text)
    await message.bot.edit_message_text(
        "Create 6-symbol unique identificator",
        chat_id=last_query.message.chat.id,
        message_id=last_query.message.message_id,
        reply_markup=return_to_achievement_menu,
    )
    await state.set_state(CreateAchievemnt.GET_ACHIEVEMENT_SHORTCUT)


# get the achievement's shortcut-code
@achievment_management_router.message(
    CreateAchievemnt.GET_ACHIEVEMENT_SHORTCUT,
    IsDirectAdminMessage(),
    F.text.regexp(r"\w{6}"),
)
async def get_achievement_shortcut(message: types.Message, state: FSMContext):
    if len(message.text) > 6:
        await message.answer("6 symbols limit")
        return 0
    state_data = await state.get_data()
    last_query = state_data["last_query"]
    achievement_name = state_data["achievement_name"]
    Achievement.create(
        achievement_name=achievement_name, achievement_shortcut=message.text
    )
    await message.answer("✅ Created")
    await message.bot.edit_message_text(
        "Choose one of the options",
        chat_id=last_query.message.chat.id,
        message_id=last_query.message.message_id,
        reply_markup=achievement_menu_settings,
    )
    await state.clear()


# open list with achievements
@achievment_management_router.callback_query(
    IsDirectAdminCallback(), F.data == "achievement_list"
)
async def show_achievement_list(query: types.CallbackQuery):
    achievements = Achievement.select()
    if achievements.exists():
        builder = InlineKeyboardBuilder()
        for achievement in achievements:
            builder.add(
                InlineKeyboardButton(
                    text=f"{achievement.achievement_name} | {achievement.achievement_shortcut}",
                    callback_data=f"achievement_id_{achievement.id}",
                )
            )
        builder.add(
            InlineKeyboardButton(text="↩️ Return", callback_data="achievement_menu")
        )
        builder.adjust(1)
        await query.bot.edit_message_text(
            "Choose achievement",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=builder.as_markup(),
        )
    else:
        await query.answer("No achievements were found")


# show achievement details
@achievment_management_router.callback_query(
    IsDirectAdminCallback(), F.data.startswith("achievement_id_")
)
async def open_achievement(query: types.CallbackQuery):
    achievement_id = int(query.data.split("_")[-1])
    achievement = Achievement.select().where(Achievement.id == achievement_id)
    if achievement.exists():
        achievement = achievement.get()
        message_text, buttons = achievement_info(achievement)
        await query.bot.edit_message_text(
            message_text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=buttons,
        )
        await query.answer()
    else:
        await query.bot.edit_message_text(
            "Choose one of the options",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=achievement_menu_settings,
        )
        await query.answer("Such achievement doesn't exist")


# delete the achievement
@achievment_management_router.callback_query(
    IsDirectAdminCallback(), F.data.startswith("achievement_delete_")
)
async def achievement_delete(query: types.CallbackQuery):
    achievement_id = int(query.data.split("_")[-1])
    achievement = MainQuest.select().where(MainQuest.id == achievement_id)
    if achievement.exists():
        achievement = achievement.get()
        achievement.delete_instance(recursive=True)
        await query.bot.edit_message_text(
            "Choose one of the options",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=achievement_menu_settings,
        )
        await query.answer("✅ Deleted successfully")
    else:
        await query.bot.edit_message_text(
            "Choose one of the options",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=achievement_menu_settings,
        )
        await query.answer("Such achievement doesn't exist")


# change the name of specific achievement
@achievment_management_router.callback_query(
    IsDirectAdminCallback(), F.data.startswith("achievement_name_change_")
)
async def achievement_name_change(query: types.CallbackQuery, state: FSMContext):
    await query.bot.edit_message_text(
        "Type the new name of the achievement",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=return_to_achievement_menu,
    )
    await state.set_data(
        {
        "last_query": query,
        "achievement_id": int(query.data.split("_")[-1])
        }
    )
    await ChangeAchievementName.GET_NEW_ACHIEVEMENT_NAME


# get the new name, and set it to achievement
@achievment_management_router.message(
    ChangeAchievementName.GET_NEW_ACHIEVEMENT_NAME,
    IsDirectAdminMessage(),
    F.text.regexp(r".+"),
)
async def achievement_name_changing(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("100 symbols limit")
        return 0
    state_data = await state.get_data()
    last_query = state_data["last_query"]
    achievement_id = state_data["achievement_id"]
    achievement = Achievement.select().where(Achievement.id == achievement_id).get()
    achievement.achievement_name = message.text
    achievement.save()
    message_text, buttons = achievement_info(achievement)
    await last_query.bot.edit_message_text(
        message_text,
        chat_id=last_query.message.chat.id,
        message_id=last_query.message.message_id,
        reply_markup=buttons,
    )
    await state.clear()
    await last_query.answer()
