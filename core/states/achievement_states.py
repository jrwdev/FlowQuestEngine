from aiogram.fsm.state import State, StatesGroup


class CreateAchievemnt(StatesGroup):
    GET_ACHIEVEMENT_NAME = State()
    GET_ACHIEVEMENT_SHORTCUT = State()


class ChangeAchievementName(StatesGroup):
    GET_NEW_ACHIEVEMENT_NAME = State()
