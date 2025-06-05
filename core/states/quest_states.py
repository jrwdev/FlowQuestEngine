from aiogram.fsm.state import State, StatesGroup


class ChooseQuestMenu(StatesGroup):
    CHOOSE_BUTTON = State()


class CreateQuest(StatesGroup):
    GET_QUEST_NAME = State()
    GET_QUEST_TEXT = State()
    GET_QUEST_ACHIEVEMENT_CODE = State()


class CreateQuestLevel(StatesGroup):
    GET_LEVEL_QUESTION = State()
    GET_LEVEL_ANSWER = State()
    GET_LEVEL_MONEY = State()
    GET_LEVEL_SKILLPOINTS = State()
    WAIT_FOR_CONFIRMATION = State()


class ChangeTextOfRiddle(StatesGroup):
    GET_NEW_TEXT_OF_RIDDLE = State()


class ChangeAnswer(StatesGroup):
    GET_NEW_ANSWER = State()


class ChangeMoneyReward(StatesGroup):
    GET_NEW_MONEY_REWARD = State()


class ChangeSkillpointsReward(StatesGroup):
    GET_NEW_SKILLPOINTS_REWARD = State()


class SolveQuest(StatesGroup):
    CHOOSE_QUEST = State()
    SOLVE_LEVEL = State()
