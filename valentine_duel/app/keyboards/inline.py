"""
Inline keyboards for bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_privacy_keyboard() -> InlineKeyboardMarkup:
    """Privacy policy acceptance keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Принимаю", callback_data="privacy_accept"),
        InlineKeyboardButton(text="📋 Читать", callback_data="privacy_read")
    )
    return builder.as_markup()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 Новая дуэль", callback_data="new_duel")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Изменить анкету", callback_data="update_questionnaire")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Призы", callback_data="view_prizes"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="my_stats")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Правила", callback_data="rules"),
        InlineKeyboardButton(text="🔒 Политика", callback_data="privacy_read")
    )
    return builder.as_markup()


def get_question_keyboard(options: list, question_index: int = 0) -> InlineKeyboardMarkup:
    """Keyboard with question options"""
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(options):
        builder.row(
            InlineKeyboardButton(
                text=option,
                callback_data=f"answer_{question_index}_{idx}"
            )
        )
    return builder.as_markup()


def get_start_duel_keyboard() -> InlineKeyboardMarkup:
    """Start duel keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 Начать дуэль", callback_data="start_duel")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_duel")
    )
    return builder.as_markup()


def get_share_results_keyboard(duel_id: int) -> InlineKeyboardMarkup:
    """Share results keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📤 Поделиться", callback_data=f"share_{duel_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Новая дуэль", callback_data="new_duel"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Back to menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel action keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    )
    return builder.as_markup()


def get_duel_start_keyboard(duel_id: int) -> InlineKeyboardMarkup:
    """Keyboard to start matched duel"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 Начать дуэль", callback_data=f"start_duel_{duel_id}")
    )
    return builder.as_markup()


def get_duel_question_keyboard(options: list, question_id: int) -> InlineKeyboardMarkup:
    """Keyboard for duel question answers"""
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.row(
            InlineKeyboardButton(
                text=option,
                callback_data=f"duel_answer_{question_id}_{option}"
            )
        )
    return builder.as_markup()


def get_duel_results_keyboard() -> InlineKeyboardMarkup:
    """Keyboard after duel completion"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Новая дуэль", callback_data="new_duel")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")
    )
    return builder.as_markup()
