from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


get_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Main menu",
                callback_data="get_to_main_menu",
            ),
        ],
    ],
    row_width=1,
)


main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Show my info",
                callback_data="show_characteristics",
            ),
        ],
        [InlineKeyboardButton(text="🚩 Quests", callback_data="show_available_quest_list")],
    ],
    row_width=1,
)


main_menu_for_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Show my info",
                callback_data="show_characteristics",
            ),
        ],
        [InlineKeyboardButton(text="🚩 Quests", callback_data="show_available_quest_list")],
        [
            InlineKeyboardButton(
                text="🔐 Admin menu",
                callback_data="admin_menu",
            ),
        ],
    ],
    row_width=1,
)


admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔍 Find player by his id",
                callback_data="search_player_by_id",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚔ Achievement settings",
                callback_data="achievement_menu",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🚩 Quest settings",
                callback_data="quest_menu",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 Main menu",
                callback_data="get_to_main_menu",
            ),
        ],
    ],
    row_width=1,
)


return_to_admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚫 Cancel",
                callback_data="admin_menu",
            ),
        ],
    ],
    row_width=1,
)


quest_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📜 List of quests", callback_data="quest_list")],
        [InlineKeyboardButton(text="🔧 Create new quest", callback_data="create_quest")],
        [InlineKeyboardButton(text="↩️ Return", callback_data="admin_menu")],
    ],
    row_width=1,
)


return_to_quest_settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚫 Cancel",
                callback_data="quest_menu",
            ),
        ],
    ],
    row_width=1,
)


skip_achievement_shortcut = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚫 Cancel",
                callback_data="quest_menu",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Skip",
                callback_data="skip_achievement_setting",
            ),
        ],
    ],
    row_width=1,
)


continue_finish_quest_creating = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="▶️ Add more",
                callback_data="continue_create",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏁 Finish",
                callback_data="finish_create",
            ),
        ],
    ],
    row_width=1,
)


continue_finish_cancel_quest_creating = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="▶️ Add more",
                callback_data="continue_create",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏁 Finish",
                callback_data="finish_create",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🚫 Cancel",
                callback_data="quest_menu",
            ),
        ],
    ],
    row_width=1,
)


achievement_menu_settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📜 List of achievements", callback_data="achievement_list")],
        [
            InlineKeyboardButton(
                text="🔧 Create new achievement", callback_data="create_achievement"
            )
        ],
        [InlineKeyboardButton(text="↩️ Return", callback_data="admin_menu")],
    ],
    row_width=1,
)

return_to_achievement_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚫 Cancel",
                callback_data="achievement_menu",
            ),
        ],
    ],
    row_width=1,
)
