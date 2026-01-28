"""
Start command and onboarding handlers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_privacy_keyboard, get_main_menu_keyboard
from app.utils.states import OnboardingStates
from app.utils.db_operations import UserRepository

router = Router()

PRIVACY_TEXT = """
🔒 <b>Политика конфиденциальности</b>

Мы собираем и обрабатываем следующие данные:
• Ваш Telegram ID
• Ваш никнейм (username)
• Ответы на вопросы анкеты
• Статистика дуэлей

Эти данные используются исключительно для работы бота и не передаются третьим лицам.

Вы можете удалить свои данные в любой момент, обратившись к администратору.
"""

RULES_TEXT = """
📋 <b>Правила игры</b>

1️⃣ Заполните анкету из 10 вопросов о своих предпочтениях
2️⃣ Пригласите друга или близкого человека на дуэль
3️⃣ Оба участника должны заполнить анкету и принять приглашение
4️⃣ В дуэли вам будет предложено 5 вопросов - угадайте, как ответил ваш соперник!
5️⃣ За каждый правильный ответ начисляются баллы
6️⃣ Победитель получает промокод, проигравший - утешительный приз (стикерпак)
7️⃣ Можете играть сколько угодно раз!

💡 Совет: чем лучше вы знаете друг друга, тем выше шансы на победу!
"""


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Get or create user
    user = await UserRepository.get_or_create_user(session, user_id, username)
    
    if not user.privacy_accepted:
        # Show privacy policy
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "🎮 Добро пожаловать в <b>Валентиновый дуэль</b> - игру для двоих!\n\n"
            "Проверьте, насколько хорошо вы знаете предпочтения друг друга. "
            "Ответьте на вопросы и сразитесь в дуэли! 💑\n\n"
            "Перед началом, пожалуйста, ознакомьтесь с политикой конфиденциальности:",
            reply_markup=get_privacy_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.waiting_for_privacy)
    else:
        # User already accepted, show main menu
        await message.answer(
            f"С возвращением, {message.from_user.first_name}! 😊\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "privacy_read")
async def show_privacy(callback: CallbackQuery):
    """Show privacy policy"""
    await callback.message.answer(
        PRIVACY_TEXT,
        reply_markup=get_privacy_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "privacy_accept")
async def accept_privacy(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Accept privacy policy"""
    user_id = callback.from_user.id
    
    # Update user
    await UserRepository.update_privacy_acceptance(session, user_id)
    
    await callback.message.edit_text(
        "✅ Спасибо! Политика конфиденциальности принята.\n\n"
        "Теперь давайте заполним вашу анкету! 📝"
    )
    
    # Clear state and redirect to questionnaire
    await state.clear()
    
    # Import here to avoid circular import
    from app.handlers.questionnaire import start_questionnaire
    await start_questionnaire(callback.message, session)


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Show main menu"""
    await state.clear()
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "rules")
async def show_rules(callback: CallbackQuery):
    """Show game rules"""
    await callback.message.answer(
        RULES_TEXT,
        parse_mode="HTML"
    )
    await callback.answer()
