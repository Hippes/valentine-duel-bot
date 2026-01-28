"""
Questionnaire handlers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_question_keyboard, get_main_menu_keyboard
from app.utils.states import QuestionnaireStates
from app.utils.db_operations import QuestionRepository, UserAnswerRepository

router = Router()


async def start_questionnaire(message: Message, session: AsyncSession, is_update: bool = False):
    """Start questionnaire process"""
    # Get all questions
    questions = await QuestionRepository.get_all_active_questions(session)
    
    if not questions:
        await message.answer(
            "😔 К сожалению, вопросы еще не добавлены. Попробуйте позже."
        )
        return
    
    # Show first question
    question = questions[0]
    await message.answer(
        f"📝 <b>Вопрос 1 из {len(questions)}</b>\n\n"
        f"{question.text}",
        reply_markup=get_question_keyboard(question.options.get('options', []), 0),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "update_questionnaire")
async def update_questionnaire_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Handle update questionnaire button"""
    await state.set_state(QuestionnaireStates.updating_answers)
    await callback.message.edit_text(
        "📝 Давайте обновим вашу анкету!\n\n"
        "Ответьте на вопросы заново."
    )
    await start_questionnaire(callback.message, session, is_update=True)
    await callback.answer()


@router.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Process questionnaire answer"""
    # Parse callback data: answer_{question_index}_{option_index}
    parts = callback.data.split("_")
    question_index = int(parts[1])
    option_index = int(parts[2])
    
    user_id = callback.from_user.id
    
    # Get all questions
    questions = await QuestionRepository.get_all_active_questions(session)
    
    if question_index >= len(questions):
        await callback.answer("Ошибка: вопрос не найден")
        return
    
    current_question = questions[question_index]
    options = current_question.options.get('options', [])
    
    if option_index >= len(options):
        await callback.answer("Ошибка: вариант ответа не найден")
        return
    
    selected_answer = options[option_index]
    
    # Save answer
    await UserAnswerRepository.save_answer(
        session, user_id, current_question.id, selected_answer
    )
    
    # Check if there are more questions
    next_index = question_index + 1
    
    if next_index < len(questions):
        # Show next question
        next_question = questions[next_index]
        await callback.message.edit_text(
            f"📝 <b>Вопрос {next_index + 1} из {len(questions)}</b>\n\n"
            f"{next_question.text}",
            reply_markup=get_question_keyboard(
                next_question.options.get('options', []),
                next_index
            ),
            parse_mode="HTML"
        )
    else:
        # Questionnaire completed
        await callback.message.edit_text(
            "✅ <b>Анкета заполнена!</b>\n\n"
            "Теперь вы можете пригласить друга на дуэль! 🎮\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
    
    await callback.answer()
