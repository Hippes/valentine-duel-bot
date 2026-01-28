"""
Duel handlers - Full implementation with matching, gameplay and results
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random
from typing import List

from app.keyboards.inline import (
    get_cancel_keyboard, 
    get_back_to_menu_keyboard,
    get_duel_start_keyboard,
    get_duel_question_keyboard,
    get_duel_results_keyboard
)
from app.utils.states import DuelStates
from app.utils.db_operations import (
    UserRepository, 
    DuelRepository, 
    UserAnswerRepository,
    QuestionRepository,
    DuelAnswerRepository
)
from app.database.models import User, Duel
from config.settings import settings

router = Router()


@router.callback_query(F.data == "new_duel")
async def start_new_duel(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Start new duel - ask for opponent username"""
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
        "Например: @username или просто username\n\n"
        "💡 <i>После ввода вы получите ссылку для приглашения</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(DuelStates.waiting_for_opponent_username)
    await callback.answer()


@router.message(DuelStates.waiting_for_opponent_username)
async def process_opponent_username(message: Message, state: FSMContext, session: AsyncSession):
    """Process opponent username and create pending duel with matching logic"""
    opponent_username = message.text.strip().replace("@", "").lower()
    user_id = message.from_user.id
    
    # Get current user
    current_user = await UserRepository.get_user(session, user_id)
    if not current_user:
        await message.answer("❌ Ошибка! Попробуйте /start")
        await state.clear()
        return
    
    # Check if trying to duel with themselves
    if current_user.username and current_user.username.lower() == opponent_username:
        await message.answer(
            "😅 Нельзя создать дуэль с самим собой!\n\n"
            "Введите username другого пользователя:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Try to find opponent in database
    opponent = await session.execute(
        select(User).where(User.username.ilike(f"%{opponent_username}%"))
    )
    opponent = opponent.scalar_one_or_none()
    
    # Check for reverse matching - has opponent already invited us?
    if opponent and opponent.id != user_id:
        # Check if opponent has pending duel waiting for us
        reverse_duel = await DuelRepository.find_pending_reverse_duel(
            session=session,
            user1_id=opponent.id,
            user2_username=current_user.username or str(user_id)
        )
        
        if reverse_duel:
            # MATCHING! Complete the reverse duel
            await DuelRepository.complete_matching(
                session=session,
                duel_id=reverse_duel.id,
                user2_id=user_id
            )
            
            await message.answer(
                f"🎉 <b>МАТЧИНГ УСПЕШЕН!</b>\n\n"
                f"Дуэль с @{opponent.username} готова!\n\n"
                f"Нажмите кнопку ниже чтобы начать игру! 🎮",
                reply_markup=get_duel_start_keyboard(reverse_duel.id),
                parse_mode="HTML"
            )
            
            # Notify opponent about matching
            try:
                await message.bot.send_message(
                    opponent.id,
                    f"🎉 <b>МАТЧИНГ УСПЕШЕН!</b>\n\n"
                    f"@{current_user.username or 'Соперник'} принял вашу дуэль!\n\n"
                    f"Нажмите кнопку ниже чтобы начать игру! 🎮",
                    reply_markup=get_duel_start_keyboard(reverse_duel.id),
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Failed to notify opponent: {e}")
            
            await state.clear()
            return
    
    # No matching - create new pending duel
    duel = await DuelRepository.create_duel(
        session=session,
        user1_id=user_id,
        user2_username=opponent_username
    )
    
    # Generate invite link
    bot_username = (await message.bot.me()).username
    invite_link = f"https://t.me/{bot_username}?start=duel_{current_user.username or user_id}"
    
    # Send invite instructions
    opponent_status = ""
    if opponent:
        opponent_answers = await UserAnswerRepository.get_user_answers(session, opponent.id)
        if len(opponent_answers) >= 10:
            opponent_status = "\n✅ @{} уже в боте и заполнил анкету!".format(opponent.username)
        else:
            opponent_status = "\n⚠️ @{} в боте, но не заполнил анкету".format(opponent.username)
    else:
        opponent_status = "\n📤 @{} еще не в боте".format(opponent_username)
    
    await message.answer(
        f"✅ <b>Запрос на дуэль создан!</b>{opponent_status}\n\n"
        f"📤 Отправьте эту ссылку @{opponent_username}:\n\n"
        f"<code>{invite_link}</code>\n\n"
        f"💡 После того как @{opponent_username}:\n"
        f"1️⃣ Перейдет по ссылке\n"
        f"2️⃣ Заполнит анкету (если еще не заполнил)\n"
        f"3️⃣ Введет ваш ник: <b>@{current_user.username or user_id}</b>\n\n"
        f"Произойдет <b>матчинг</b> и дуэль начнется! 🎮",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    
    await state.clear()


@router.callback_query(F.data.startswith("start_duel_"))
async def start_duel_game(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Start the duel game - select 5 random questions and begin"""
    duel_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    # Get duel
    duel = await DuelRepository.get_duel(session, duel_id)
    
    if not duel:
        await callback.answer("❌ Дуэль не найдена!", show_alert=True)
        return
    
    if duel.status == "completed":
        await callback.answer("❌ Дуэль уже завершена!", show_alert=True)
        return
    
    # Check if user is participant
    if user_id not in [duel.user1_id, duel.user2_id]:
        await callback.answer("❌ Вы не участник этой дуэли!", show_alert=True)
        return
    
    # If duel is matched but not started yet - select questions and start
    if duel.status == "matched" and not duel.selected_questions:
        # Select 5 random questions
        all_questions = await QuestionRepository.get_all_questions(session)
        if len(all_questions) < 5:
            await callback.answer("❌ Недостаточно вопросов в базе!", show_alert=True)
            return
        
        selected_questions = random.sample([q.id for q in all_questions], 5)
        
        # Update duel with selected questions and start
        await DuelRepository.start_duel(session, duel_id, selected_questions)
        duel = await DuelRepository.get_duel(session, duel_id)
    
    # Check if user already answered all questions
    user_answers = await DuelAnswerRepository.get_user_duel_answers(session, duel_id, user_id)
    if len(user_answers) >= 5:
        await callback.answer("✅ Вы уже ответили на все вопросы! Ждем соперника...", show_alert=True)
        return
    
    # Send first unanswered question
    question_index = len(user_answers)
    await send_duel_question(callback.message, session, duel_id, user_id, question_index, state)
    await callback.answer()


async def send_duel_question(message: Message, session: AsyncSession, duel_id: int, user_id: int, question_index: int, state: FSMContext):
    """Send a duel question to user"""
    # Get duel
    duel = await DuelRepository.get_duel(session, duel_id)
    question_id = duel.selected_questions[question_index]
    
    # Get question
    question = await QuestionRepository.get_question(session, question_id)
    
    # Get opponent
    opponent_id = duel.user2_id if user_id == duel.user1_id else duel.user1_id
    opponent = await UserRepository.get_user(session, opponent_id)
    
    # Format question
    text = (
        f"🎮 <b>ДУЭЛЬ</b>\n\n"
        f"❓ <b>Вопрос {question_index + 1} из 5</b>\n\n"
        f"{question.text}\n\n"
        f"🤔 <b>Как вы думаете, что ответил @{opponent.username or 'соперник'}?</b>"
    )
    
    # Save state
    await state.update_data(
        duel_id=duel_id,
        current_question=question_index,
        question_id=question_id
    )
    await state.set_state(DuelStates.answering_duel_questions)
    
    await message.answer(
        text,
        reply_markup=get_duel_question_keyboard(question.options, question_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("duel_answer_"))
async def process_duel_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Process duel answer and move to next question or finish"""
    data = await state.get_data()
    duel_id = data.get("duel_id")
    current_question_index = data.get("current_question")
    question_id = data.get("question_id")
    
    # Parse answer
    _, _, qid, answer = callback.data.split("_", 3)
    user_id = callback.from_user.id
    
    # Save answer
    await DuelAnswerRepository.create_answer(
        session=session,
        duel_id=duel_id,
        user_id=user_id,
        question_id=question_id,
        guessed_answer=answer
    )
    
    # Check if there are more questions
    if current_question_index < 4:
        # Send next question
        await callback.message.delete()
        await send_duel_question(callback.message, session, duel_id, user_id, current_question_index + 1, state)
    else:
        # Finished answering
        await callback.message.edit_text(
            "✅ <b>Вы ответили на все вопросы!</b>\n\n"
            "⏳ Ожидаем ответов соперника...\n\n"
            "Как только соперник завершит дуэль, вы получите результаты! 📊",
            parse_mode="HTML"
        )
        await state.clear()
        
        # Check if opponent also finished
        await check_and_finish_duel(session, duel_id, callback.bot)
    
    await callback.answer()


async def check_and_finish_duel(session: AsyncSession, duel_id: int, bot):
    """Check if both users finished and calculate results"""
    duel = await DuelRepository.get_duel(session, duel_id)
    
    # Get answers count for both users
    user1_answers = await DuelAnswerRepository.get_user_duel_answers(session, duel_id, duel.user1_id)
    user2_answers = await DuelAnswerRepository.get_user_duel_answers(session, duel_id, duel.user2_id)
    
    # Check if both finished (5 answers each)
    if len(user1_answers) == 5 and len(user2_answers) == 5:
        # Calculate scores
        user1_score = await calculate_score(session, duel.user1_id, duel.user2_id, user1_answers)
        user2_score = await calculate_score(session, duel.user2_id, duel.user1_id, user2_answers)
        
        # Update duel with scores and complete
        await DuelRepository.finish_duel(session, duel_id, user1_score, user2_score)
        
        # Send results to both users
        await send_results(bot, session, duel, user1_score, user2_score)


async def calculate_score(session: AsyncSession, user_id: int, opponent_id: int, answers: List) -> int:
    """Calculate score for user by comparing guesses with opponent's real answers"""
    score = 0
    
    # Get opponent's real answers from questionnaire
    opponent_answers = await UserAnswerRepository.get_user_answers(session, opponent_id)
    opponent_answers_dict = {a.question_id: a.answer for a in opponent_answers}
    
    for answer in answers:
        question = await QuestionRepository.get_question(session, answer.question_id)
        real_answer = opponent_answers_dict.get(answer.question_id)
        
        if real_answer and answer.guessed_answer == real_answer:
            # Correct guess!
            points = question.weight
            score += points
            # Mark answer as correct
            await DuelAnswerRepository.mark_correct(session, answer.id, points)
    
    return score


async def send_results(bot, session: AsyncSession, duel: Duel, user1_score: int, user2_score: int):
    """Send duel results to both users with prizes"""
    user1 = await UserRepository.get_user(session, duel.user1_id)
    user2 = await UserRepository.get_user(session, duel.user2_id)
    
    # Determine winner
    if user1_score > user2_score:
        winner_text = f"🏆 Победитель: @{user1.username or 'User 1'}"
        user1_is_winner = True
    elif user2_score > user1_score:
        winner_text = f"🏆 Победитель: @{user2.username or 'User 2'}"
        user1_is_winner = False
    else:
        winner_text = "🤝 Ничья!"
        user1_is_winner = None
    
    # Format results for user1
    user1_result = "🏆 <b>ПОБЕДА!</b>" if user1_is_winner else ("😔 <b>Поражение</b>" if user1_is_winner is False else "🤝 <b>Ничья!</b>")
    user1_prize = ""
    if user1_is_winner:
        user1_prize = f"\n\n🎁 <b>Ваш приз:</b>\nПромокод: <code>{settings.PROMO_CODE}</code>"
    elif user1_is_winner is False:
        user1_prize = f"\n\n💝 <b>Утешительный приз:</b>\nСтикерпак: {settings.STICKER_PACK_URL}"
    
    # Format results for user2
    user2_result = "🏆 <b>ПОБЕДА!</b>" if not user1_is_winner and user1_is_winner is not None else ("😔 <b>Поражение</b>" if user1_is_winner else "🤝 <b>Ничья!</b>")
    user2_prize = ""
    if not user1_is_winner and user1_is_winner is not None:
        user2_prize = f"\n\n🎁 <b>Ваш приз:</b>\nПромокод: <code>{settings.PROMO_CODE}</code>"
    elif user1_is_winner:
        user2_prize = f"\n\n💝 <b>Утешительный приз:</b>\nСтикерпак: {settings.STICKER_PACK_URL}"
    
    # Send to user1
    try:
        await bot.send_message(
            duel.user1_id,
            f"{user1_result}\n\n"
            f"📊 <b>Результаты дуэли</b>\n\n"
            f"Вы: <b>{user1_score}</b> баллов\n"
            f"@{user2.username or 'Соперник'}: <b>{user2_score}</b> баллов\n\n"
            f"{winner_text}"
            f"{user1_prize}",
            reply_markup=get_duel_results_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Failed to send results to user1: {e}")
    
    # Send to user2
    try:
        await bot.send_message(
            duel.user2_id,
            f"{user2_result}\n\n"
            f"📊 <b>Результаты дуэли</b>\n\n"
            f"Вы: <b>{user2_score}</b> баллов\n"
            f"@{user1.username or 'Соперник'}: <b>{user1_score}</b> баллов\n\n"
            f"{winner_text}"
            f"{user2_prize}",
            reply_markup=get_duel_results_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Failed to send results to user2: {e}")


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "view_prizes")
async def view_prizes(callback: CallbackQuery):
    """Show available prizes"""
    await callback.message.edit_text(
        "🎁 <b>Призы</b>\n\n"
        f"🏆 <b>Победителю:</b>\n"
        f"Промокод: <code>{settings.PROMO_CODE}</code>\n\n"
        f"💝 <b>Проигравшему:</b>\n"
        f"Стикерпак: {settings.STICKER_PACK_URL}",
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
    answers_count = len(answers)
    questionnaire_complete = "✅ Заполнена" if answers_count >= 10 else f"⚠️ Заполнено {answers_count}/10"
    
    # Get duel stats
    user_duels = await DuelRepository.get_user_duels(session, user_id)
    total_duels = len(user_duels)
    completed_duels = len([d for d in user_duels if d.status == "completed"])
    
    wins = 0
    for duel in user_duels:
        if duel.status == "completed":
            if duel.user1_id == user_id and duel.user1_score > duel.user2_score:
                wins += 1
            elif duel.user2_id == user_id and duel.user2_score > duel.user1_score:
                wins += 1
    
    await callback.message.edit_text(
        f"📊 <b>Ваша статистика</b>\n\n"
        f"📝 Анкета: {questionnaire_complete}\n"
        f"🎮 Дуэлей сыграно: {completed_duels}\n"
        f"🏆 Побед: {wins}\n"
        f"📈 Процент побед: {int(wins/completed_duels*100) if completed_duels > 0 else 0}%",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
