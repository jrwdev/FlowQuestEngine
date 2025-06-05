from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_player_characteristics(player):
    skill_designation = ""
    if 0 <= player.player_skill_level <= 30:
        skill_designation = "newbie"
    elif 30 < player.player_skill_level <= 100:
        skill_designation = "skilled"
    elif player.player_skill_level > 100:
        skill_designation = "master 🛡"
    fullname = player.player_full_name
    player_id = player.player_telegram_id
    balance = player.player_balance
    skill_points = player.player_skill_points
    next_level_points = player.player_skill_points_to_next_level
    skill_level = player.player_skill_level
    reg_date = str(player.player_joined_date.date()).replace("-", ".")
    if player.player_ban:
        ban_status = "Yes"
    else:
        ban_status = "No"
    return f"📜 Player name:\n    <code>{fullname}</code>\n\n💳 Your id:\n    <code>{player_id}</code>\n\n💰 Balance:\n    <code>{balance}</code> 🔑\n\n⚔️ Level:\n    <code>{skill_points}/{next_level_points} - level {skill_level}</code> (<em>{skill_designation}</em>)\n\n🗓 Registration date:\n    <code>{reg_date}</code> (<em>yyyy.mm.dd</em>)\n\n⚖️ Banned  -  <code>{ban_status}</code>"


def update_player_information(player, message):
    exist_player = player.get()
    if message.from_user.username is None:
        exist_player.player_username = None
    else:
        exist_player.player_username = message.from_user.username
    exist_player.player_full_name = message.from_user.full_name
    exist_player.save()


def create_new_player(player, message):
    player.create(
        player_telegram_id=message.from_user.id,
        player_username=message.from_user.username,
        player_full_name=message.from_user.full_name,
    )


def player_settings(player):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="💰 Edit balance",
            callback_data=f"change_player_balance_{player.player_telegram_id}",
        ),
        InlineKeyboardButton(
            text="⚔️ Edit level",
            callback_data=f"change_player_skill_points_{player.player_telegram_id}",
        ),
    )
    if player.player_ban:
        builder.add(
            InlineKeyboardButton(
                text="📗 Unban",
                callback_data=f"unban_player_{player.player_telegram_id}",
            )
        )
    else:
        builder.add(
            InlineKeyboardButton(
                text="📕 Ban",
                callback_data=f"ban_player_{player.player_telegram_id}",
            )
        )
    builder.add(
        InlineKeyboardButton(text="🗑 Admin menu", callback_data=f"admin_menu")
    )
    characteristics = get_player_characteristics(player)
    builder.adjust(3)
    return characteristics, builder.as_markup()


# calculating level from skill points
def skill_level_calculator(skill_points):
    a = 20  # default first-level points
    d = 2  # increment steps
    points_to_rich_level = 20  # status of points to get next level
    points_to_next_level = 0  # another status
    level = 0  # level status

    while True:
        if points_to_rich_level > skill_points:
            break
        elif points_to_rich_level == skill_points:
            level += 1
            break
        elif points_to_rich_level < skill_points:
            a += d
            points_to_rich_level += a
            level += 1

    if points_to_rich_level == skill_points:
        points_to_next_level = points_to_rich_level + (a + d)
        return level, points_to_next_level
    else:
        return level, points_to_rich_level
