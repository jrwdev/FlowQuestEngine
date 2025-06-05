from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.db.models import QuestLevel, Achievement


def getting_main_quest_info(quest):
    builder = InlineKeyboardBuilder()
    main_quest_name = quest.quest_name
    main_quest_text = quest.quest_text
    if quest.quest_achievement:
        achievement = Achievement.select().where(
            Achievement.achievement_shortcut == quest.quest_achievement
        )
        if achievement.exists:
            achievement = achievement.get()
            main_quest_achievement = (
                f"{achievement.achievement_name} | {achievement.achievement_shortcut}"
            )
        else:
            main_quest_achievement = "Empty"
    else:
        main_quest_achievement = "Empty"
    if quest.quest_publish:
        publish_status = "✅ Published"
        builder.add(
            InlineKeyboardButton(text="🔘 Unpublish", callback_data=f"unpublish_{quest.id}")
        )
    else:
        publish_status = "♻️ Pending publication"
        builder.add(
            InlineKeyboardButton(
                text="✅ Publish", callback_data=f"publish_{quest.id}"
            )
        )
    quest_levels = (
        QuestLevel.select()
        .where(QuestLevel.main_quest == quest)
        .order_by(QuestLevel.level_number)
    )
    for level in quest_levels:
        if level.level_last_status:
            builder.add(
                InlineKeyboardButton(
                    text=f"⚫️ level {level.level_number}",
                    callback_data=f"level_id_{level.id}",
                )
            )
        else:
            builder.add(
                InlineKeyboardButton(
                    text=f"⚪️ level {level.level_number}",
                    callback_data=f"level_id_{level.id}",
                )
            )
    builder.add(
        InlineKeyboardButton(
            text="🗑 Delete", callback_data=f"quest_delete_{quest.id}"
        ),
        InlineKeyboardButton(text="↩️ Go back", callback_data="quest_list"),
    )
    message_text = f"Name:\n{main_quest_name}\n\nDescription:\n{main_quest_text}\n\nAchievement: {main_quest_achievement}\n\nStatus of publication: {publish_status}"
    builder.adjust(1)
    return message_text, builder.as_markup()


def getting_quest_level_info(level):
    builder = InlineKeyboardBuilder()
    level_main_quest = level.main_quest
    level_number = level.level_number
    level_question = level.level_question
    level_answer = level.level_answer
    level_reward = level.level_reward_money
    level_skill = level.level_reward_skill
    level_status = level.level_last_status
    if level_status:
        level_status = "🏁 Final level"
    else:
        level_status = "🏳️ Usual level"
    message_text = f"Quest name: {level_main_quest.quest_name}\n\nLevel number: {level_number}\n\nLevel question:\n{level_question}\n\nAnswer:\n{level_answer}\n\nReward:\n{level_reward} coins 🔑\n{level_skill} skill points ⚔\n\nStatus: {level_status}"
    builder.add(
        InlineKeyboardButton(
            text="Edit question", callback_data=f"riddle_text_change_{level.id}"
        ),
        InlineKeyboardButton(
            text="Edit answer", callback_data=f"answer_change_{level.id}"
        ),
        InlineKeyboardButton(
            text="Edit coin reward", callback_data=f"reward_change_{level.id}"
        ),
        InlineKeyboardButton(
            text="Edit skill point reward", callback_data=f"skill_change_{level.id}"
        ),
        InlineKeyboardButton(text="↩️ Go back", callback_data="quest_menu"),
    )
    builder.adjust(2)
    return message_text, builder.as_markup()


def achievement_info(achievement):
    builder = InlineKeyboardBuilder()
    message_text = (
        f"{achievement.achievement_name} | {achievement.achievement_shortcut}"
    )
    builder.add(
        InlineKeyboardButton(
            text="📝 Change name",
            callback_data=f"achievement_name_change_{achievement.id}",
        ),
        InlineKeyboardButton(
            text="🗑 Delete", callback_data=f"achievement_delete_{achievement.id}"
        ),
        InlineKeyboardButton(text="↩️ Go back", callback_data="achievement_menu"),
    )
    builder.adjust(1)
    return message_text, builder.as_markup()
