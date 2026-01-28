"""
Database operations utilities
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, Question, UserAnswer, Duel, DuelAnswer


class UserRepository:
    """User database operations"""
    
    @staticmethod
    async def create_user(session: AsyncSession, user_id: int, username: Optional[str] = None) -> User:
        """Create new user"""
        user = User(id=user_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_privacy_acceptance(session: AsyncSession, user_id: int) -> None:
        """Update user's privacy acceptance"""
        await session.execute(
            update(User).where(User.id == user_id).values(privacy_accepted=True)
        )
        await session.commit()
    
    @staticmethod
    async def get_or_create_user(session: AsyncSession, user_id: int, username: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        user = await UserRepository.get_user(session, user_id)
        if not user:
            user = await UserRepository.create_user(session, user_id, username)
        return user


class QuestionRepository:
    """Question database operations"""
    
    @staticmethod
    async def get_all_active_questions(session: AsyncSession) -> List[Question]:
        """Get all active questions"""
        result = await session.execute(
            select(Question).where(Question.is_active == True).order_by(Question.id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_question_by_id(session: AsyncSession, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        result = await session.execute(select(Question).where(Question.id == question_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_random_questions(session: AsyncSession, count: int = 5) -> List[Question]:
        """Get random active questions"""
        result = await session.execute(
            select(Question)
            .where(Question.is_active == True)
            .order_by(func.random())
            .limit(count)
        )
        return list(result.scalars().all())


class UserAnswerRepository:
    """User answer database operations"""
    
    @staticmethod
    async def save_answer(
        session: AsyncSession,
        user_id: int,
        question_id: int,
        answer: str
    ) -> UserAnswer:
        """Save or update user's answer"""
        # Check if answer exists
        result = await session.execute(
            select(UserAnswer).where(
                and_(UserAnswer.user_id == user_id, UserAnswer.question_id == question_id)
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing answer
            await session.execute(
                update(UserAnswer)
                .where(UserAnswer.id == existing.id)
                .values(answer=answer, updated_at=datetime.utcnow())
            )
            await session.commit()
            result = await session.execute(select(UserAnswer).where(UserAnswer.id == existing.id))
            return result.scalar_one()
        else:
            # Create new answer
            user_answer = UserAnswer(user_id=user_id, question_id=question_id, answer=answer)
            session.add(user_answer)
            await session.commit()
            await session.refresh(user_answer)
            return user_answer
    
    @staticmethod
    async def get_user_answers(session: AsyncSession, user_id: int) -> List[UserAnswer]:
        """Get all user's answers"""
        result = await session.execute(
            select(UserAnswer)
            .where(UserAnswer.user_id == user_id)
            .options(selectinload(UserAnswer.question))
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_answer(
        session: AsyncSession,
        user_id: int,
        question_id: int
    ) -> Optional[UserAnswer]:
        """Get specific user answer"""
        result = await session.execute(
            select(UserAnswer).where(
                and_(UserAnswer.user_id == user_id, UserAnswer.question_id == question_id)
            )
        )
        return result.scalar_one_or_none()


class DuelRepository:
    """Duel database operations"""
    
    @staticmethod
    async def create_duel(
        session: AsyncSession,
        user1_id: int,
        user2_id: int
    ) -> Duel:
        """Create new duel"""
        duel = Duel(user1_id=user1_id, user2_id=user2_id, status="pending")
        session.add(duel)
        await session.commit()
        await session.refresh(duel)
        return duel
    
    @staticmethod
    async def get_duel_by_id(session: AsyncSession, duel_id: int) -> Optional[Duel]:
        """Get duel by ID"""
        result = await session.execute(
            select(Duel)
            .where(Duel.id == duel_id)
            .options(selectinload(Duel.user1), selectinload(Duel.user2))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_duel_for_user(session: AsyncSession, user_id: int) -> Optional[Duel]:
        """Get active duel for user"""
        result = await session.execute(
            select(Duel)
            .where(
                and_(
                    (Duel.user1_id == user_id) | (Duel.user2_id == user_id),
                    Duel.status.in_(["pending", "active"])
                )
            )
            .order_by(Duel.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_duel_status(
        session: AsyncSession,
        duel_id: int,
        status: str,
        selected_questions: Optional[List[int]] = None
    ) -> None:
        """Update duel status"""
        values = {"status": status}
        if selected_questions:
            values["selected_questions"] = {"question_ids": selected_questions}
        
        await session.execute(update(Duel).where(Duel.id == duel_id).values(**values))
        await session.commit()
    
    @staticmethod
    async def complete_duel(
        session: AsyncSession,
        duel_id: int,
        user1_score: int,
        user2_score: int
    ) -> None:
        """Complete duel with scores"""
        await session.execute(
            update(Duel)
            .where(Duel.id == duel_id)
            .values(
                status="completed",
                user1_score=user1_score,
                user2_score=user2_score,
                completed_at=datetime.utcnow()
            )
        )
        await session.commit()
    
    @staticmethod
    async def cancel_duel(session: AsyncSession, duel_id: int) -> None:
        """Cancel duel"""
        await session.execute(
            update(Duel).where(Duel.id == duel_id).values(status="cancelled")
        )
        await session.commit()


class DuelAnswerRepository:
    """Duel answer database operations"""
    
    @staticmethod
    async def save_duel_answer(
        session: AsyncSession,
        duel_id: int,
        user_id: int,
        question_id: int,
        guessed_answer: str
    ) -> DuelAnswer:
        """Save duel answer"""
        duel_answer = DuelAnswer(
            duel_id=duel_id,
            user_id=user_id,
            question_id=question_id,
            guessed_answer=guessed_answer
        )
        session.add(duel_answer)
        await session.commit()
        await session.refresh(duel_answer)
        return duel_answer
    
    @staticmethod
    async def get_user_duel_answers(
        session: AsyncSession,
        duel_id: int,
        user_id: int
    ) -> List[DuelAnswer]:
        """Get user's answers for specific duel"""
        result = await session.execute(
            select(DuelAnswer)
            .where(and_(DuelAnswer.duel_id == duel_id, DuelAnswer.user_id == user_id))
            .options(selectinload(DuelAnswer.question))
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def check_and_score_answers(
        session: AsyncSession,
        duel_id: int,
        user_id: int,
        opponent_id: int
    ) -> int:
        """Check answers and calculate score"""
        # Get user's guesses
        duel_answers = await DuelAnswerRepository.get_user_duel_answers(session, duel_id, user_id)
        
        total_score = 0
        for duel_answer in duel_answers:
            # Get opponent's actual answer
            opponent_answer = await UserAnswerRepository.get_user_answer(
                session, opponent_id, duel_answer.question_id
            )
            
            if opponent_answer and duel_answer.guessed_answer == opponent_answer.answer:
                # Correct guess
                question = await QuestionRepository.get_question_by_id(session, duel_answer.question_id)
                points = question.weight if question else 1
                total_score += points
                
                # Update duel answer
                await session.execute(
                    update(DuelAnswer)
                    .where(DuelAnswer.id == duel_answer.id)
                    .values(is_correct=True, points_earned=points)
                )
            else:
                # Wrong guess
                await session.execute(
                    update(DuelAnswer)
                    .where(DuelAnswer.id == duel_answer.id)
                    .values(is_correct=False, points_earned=0)
                )
        
        await session.commit()
        return total_score
