"""
Finite State Machine states for bot
"""
from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Onboarding flow states"""
    waiting_for_privacy = State()


class QuestionnaireStates(StatesGroup):
    """Questionnaire filling states"""
    answering_questions = State()
    updating_answers = State()


class DuelStates(StatesGroup):
    """Duel flow states"""
    waiting_for_opponent_username = State()
    waiting_to_start = State()
    answering_duel_questions = State()
    waiting_for_opponent_finish = State()
