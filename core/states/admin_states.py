from aiogram.fsm.state import State, StatesGroup


class FindPlayer(StatesGroup):
    GET_PLAYER_ID = State()
    WAIT_FOR_NEXT_STATE = State()


class ChangeSkillPoints(StatesGroup):
    GET_SKILL_POINTS = State()
    WAIT_FOR_NEXT_STATE = State()


class ChangeBalance(StatesGroup):
    GET_NEW_BALANCE = State()
    WAIT_FOR_NEXT_STATE = State()


class WaitForNextState(StatesGroup):
    WAIT_FOR_NEXT_STATE = State()
