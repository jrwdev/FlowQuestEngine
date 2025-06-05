from aiogram import types, F, Router
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


from core.db.models import (
    Player,
    MainQuest,
    PlayerAnswer,
    QuestLevel,
    Achievement,
    PlayerAchievement,
)
from core.keyboards.inline import main_menu, main_menu_for_admin
from core.utils.player_utils import skill_level_calculator
from core.filters.filters import check_for_admin, IsDirectCallback, IsDirectMessage
from core.states.quest_states import SolveQuest


quest_interaction_commands_router = Router()


#  open list of all available quests
@quest_interaction_commands_router.callback_query(
    IsDirectCallback(), F.data == "show_available_quest_list"
)
async def show_available_quests(query: types.CallbackQuery, state: FSMContext = None):
    builder = InlineKeyboardBuilder()
    quests = MainQuest.select().where(MainQuest.quest_publish == True)
    if quests.exists():
        for quest in quests:
            builder.add(
                InlineKeyboardButton(
                    text=f"{quest.quest_name}",
                    callback_data=f"start_solve_quest_{quest.id}",
                )
            )
        builder.add(
            InlineKeyboardButton(
                text="📋 Main menu", callback_data="get_to_main_menu"
            )
        )
        builder.adjust(1)
        await query.bot.edit_message_text(
            "To start, choose one of the following quests:",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=builder.as_markup(),
        )
        await state.set_state(SolveQuest.CHOOSE_QUEST)
        await query.answer()
    else:
        await query.answer("No quests available yet. Try again later.")


#  handler for starting to solve quest
@quest_interaction_commands_router.callback_query(
    SolveQuest.CHOOSE_QUEST, IsDirectCallback(), F.data.startswith("start_solve_quest_")
)
async def start_solving_quest(query: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    quest_id = int(query.data.split("_")[-1])
    quest = MainQuest.select().where(MainQuest.id == quest_id)
    if quest.exists():
        quest = quest.get()
        player = (
            Player.select().where(Player.player_telegram_id == query.from_user.id).get()
        )
        player_answers = (
            PlayerAnswer.select()
            .where(
                (PlayerAnswer.player == player)
                & (PlayerAnswer.answered_main_quest == quest)
            )
            .order_by(PlayerAnswer.answered_level_number)
        )
        if player_answers.exists():
            last_answer = player_answers[-1]
            last_solved_level = last_answer.answered_question
            if last_solved_level.level_last_status:
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
                await query.answer("👑 You have completed the quest! Congratulations!")
            else:
                next_level_number = last_solved_level.level_number + 1
                quest_level = (
                    QuestLevel.select()
                    .where(
                        (QuestLevel.main_quest == quest)
                        & (QuestLevel.level_number == next_level_number)
                    )
                    .get()
                )
                await state.update_data(
                    quest_level_id=quest_level.id, message=query.message
                )
                message_text = (
                    f"Level {quest_level.level_number}\n\n{quest_level.level_question}"
                )
                builder.add(
                    InlineKeyboardButton(
                        text="↩️ Back", callback_data="get_to_main_menu"
                    )
                )
                builder.adjust(1)
                await query.bot.edit_message_text(
                    message_text,
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id,
                    reply_markup=builder.as_markup(),
                )
                await state.set_state(SolveQuest.SOLVE_LEVEL)
                await query.answer()
        else:
            quest_level = (
                QuestLevel.select()
                .where(
                    (QuestLevel.main_quest == quest) & (QuestLevel.level_number == 1)
                )
                .get()
            )
            await state.update_data(
                quest_level_id=quest_level.id, message=query.message
            )
            message_text = f"{quest.quest_text}\n\nLevel {quest_level.level_number}\n\n{quest_level.level_question}"
            builder.add(
                InlineKeyboardButton(text="↩️ Back", callback_data="get_to_main_menu")
            )
            builder.adjust(1)
            await query.bot.edit_message_text(
                message_text,
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=builder.as_markup(),
            )
            await state.set_state(SolveQuest.SOLVE_LEVEL)
            await query.answer()
    else:
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
        await query.answer("No quests available yet. Try again later.")


# getting the answer to quest level
@quest_interaction_commands_router.message(
    SolveQuest.SOLVE_LEVEL, IsDirectMessage(), F.text.regexp(r".+")
)
async def getting_answer_to_quest_level(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    info = await state.get_data()
    quest_level_id = info["quest_level_id"]
    last_message = info["message"]
    level = QuestLevel.select().where(QuestLevel.id == quest_level_id)
    if level.exists():
        level = level.get()
        main_quest = level.main_quest
        if level.level_answer == message.text.lower():
            player = (
                Player.select()
                .where(Player.player_telegram_id == message.from_user.id)
                .get()
            )
            PlayerAnswer.create(
                player=player,
                answered_main_quest=main_quest,
                answered_question=level,
                answered_level_number=level.level_number,
            )
            player.player_balance += level.level_reward_money
            player.player_skill_points += level.level_reward_skill
            if player.player_skill_points > player.player_skill_points_to_next_level:
                new_level, points_to_next_level = skill_level_calculator(
                    player.player_skill_points
                )
                player.player_skill_level = new_level
                player.player_skill_points_to_next_level = points_to_next_level
            player.save()
            await message.answer(
                f"🎉 correct answer! You passed the level!\n\nYou get:\n{level.level_reward_money} experience 🔑\n{level.level_reward_skill} skill points ⚔"
            )
            if level.level_last_status:
                await message.answer("👑 Congratulations! You have completed the quest!")
                if main_quest.quest_achievement:
                    achievement = Achievement.select().where(
                        Achievement.achievement_shortcut == main_quest.quest_achievement
                    )
                    if achievement.exists():
                        achievement = achievement.get()
                        PlayerAchievement.create(player=player, achievement=achievement)
                        await message.answer(
                            f'Achievement: "{achievement.achievement_name}"'
                        )
                await state.clear()
                mm = main_menu
                if check_for_admin(admin_id=message.from_user.id):
                    mm = main_menu_for_admin
                await message.bot.delete_message(
                    chat_id=last_message.chat.id, message_id=last_message.message_id
                )
                await message.bot.send_message(
                    chat_id=message.chat.id,
                    text="Choose one of the menu options:",
                    reply_markup=mm,
                )
            else:
                next_level_number = level.level_number + 1
                next_level = (
                    QuestLevel.select()
                    .where(
                        (QuestLevel.main_quest == main_quest)
                        & (QuestLevel.level_number == next_level_number)
                    )
                    .get()
                )
                message_text = (
                    f"Level {next_level.level_number}\n\n{next_level.level_question}"
                )
                builder.add(
                    InlineKeyboardButton(
                        text="↩️ Back", callback_data="get_to_main_menu"
                    )
                )
                await message.bot.delete_message(
                    chat_id=last_message.chat.id, message_id=last_message.message_id
                )
                builder.adjust(1)
                last_message = await message.bot.send_message(
                    chat_id=message.chat.id,
                    text=message_text,
                    reply_markup=builder.as_markup(),
                )
                await state.update_data(
                    quest_level_id=next_level.id, message=last_message
                )
                await state.set_state(SolveQuest.SOLVE_LEVEL)
        else:
            await message.answer("Wrong answer. Think more!")
            await state.set_state(SolveQuest.SOLVE_LEVEL)
    else:
        await state.clear()
        mm = main_menu
        if check_for_admin(admin_id=message.from_user.id):
            mm = main_menu_for_admin
        await message.bot.delete_message(
            chat_id=last_message.chat.id, message_id=last_message.message_id
        )
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Choose one of the menu options:",
            reply_markup=mm,
        )
        await message.answer("No quests available yet. Try again later.")
