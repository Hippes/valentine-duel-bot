"""
Duel handlers
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_cancel_keyboard, get_back_to_menu_keyboard
from app.utils.states import DuelStates
from app.utils.db_operations import UserRepository, DuelRepository, UserAnswerRepository

router = Router()


@router.callback_query(F.data == "new_duel")
async def start_new_duel(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Start new duel"""
    user_id = callback.from_user.id
    
    # Check if user has filled questionnaire
    answers = await UserAnswerRepository.get_user_answers(session, user_id)
    
    if len(answers) < 10:
        await callback.message.answer(
            "❌ Сначала заполните анкету!\n\n"
            "Нажмите 📝 Изменить анкету в меню.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Check if user already has active duel
    active_duel = await DuelRepository.get_active_duel_for_user(session, user_id)
    
    if active_duel:
        await callback.message.answer(
            "⚠️ У вас уже есть активная дуэль!\n\n"
            "Завершите её или отмените перед созданием новой.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Ask for opponent username
    await callback.message.edit_text(
        "🎮 <b>Новая дуэль</b>\n\n"
        "Введите @username вашего соперника:\n\n"
        "Например: @username или просто username",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(DuelStates.waiting_for_opponent_username)
    await callback.answer()


@router.message(DuelStates.waiting_for_opponent_username)
async def process_opponent_username(message: Message, state: FSMContext, session: AsyncSession):
    """Process opponent username"""
    opponent_username = message.text.strip().replace("@", "")
    user_id = message.from_user.id
    
    await message.answer(
        "🚧 <b>Функция в разработке</b>\n\n"
        "Механика дуэлей будет добавлена в следующем обновлении!\n\n"
        "Пока доступны:\n"
        "✅ Регистрация\n"
        "✅ Заполнение анкеты\n"
        "✅ Изменение анкеты\n\n"
        "Следите за обновлениями! 🎉",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await state.clear()
    
    from app.keyboards.inline import get_main_menu_keyboard
    await callback.message.edit_text(
        "❌ Действие отменено.\n\n"
        "🏠 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "view_prizes")
async def view_prizes(callback: CallbackQuery):
    """View prizes"""
    from config.settings import settings
    
    await callback.message.answer(
        "🎁 <b>Призы</b>\n\n"
        f"🏆 <b>Для победителя:</b>\n"
        f"Промокод: <code>{settings.PROMO_CODE}</code>\n"
        f"(нажмите чтобы скопировать)\n\n"
        f"💝 <b>Для проигравшего:</b>\n"
        f"Стикерпак: {settings.STICKER_PACK_URL}\n\n"
        f"Играйте и выигрывайте! 🎮",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "my_stats")
async def my_stats(callback: CallbackQuery, session: AsyncSession):
    """Show user statistics"""
    user_id = callback.from_user.id
    
    # Get user answers count
    answers = await UserAnswerRepository.get_user_answers(session, user_id)
    
    await callback.message.answer(
        "📊 <b>Ваша статистика</b>\n\n"
        f"✅ Анкета заполнена: {'Да' if len(answers) >= 10 else 'Нет'}\n"
        f"📝 Ответов на вопросы: {len(answers)}\n\n"
        f"🚧 Статистика дуэлей будет доступна в следующем обновлении!",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
