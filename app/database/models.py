"""
Database models for Valentine Duel Bot
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, String, Boolean, Integer, JSON, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    privacy_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    answers: Mapped[List["UserAnswer"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    duels_as_user1: Mapped[List["Duel"]] = relationship(
        foreign_keys="Duel.user1_id", back_populates="user1", cascade="all, delete-orphan"
    )
    duels_as_user2: Mapped[List["Duel"]] = relationship(
        foreign_keys="Duel.user2_id", back_populates="user2", cascade="all, delete-orphan"
    )
    duel_answers: Mapped[List["DuelAnswer"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Question(Base):
    """Question model"""
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)  # List of answer options
    weight: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user_answers: Mapped[List["UserAnswer"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    duel_answers: Mapped[List["DuelAnswer"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, text={self.text[:30]}...)>"


class UserAnswer(Base):
    """User's answers to profile questionnaire"""
    __tablename__ = "user_answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="user_answers")
    
    def __repr__(self):
        return f"<UserAnswer(user_id={self.user_id}, question_id={self.question_id}, answer={self.answer})>"


class Duel(Base):
    """Duel model"""
    __tablename__ = "duels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending, active, completed, cancelled
    selected_questions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # List of 5 question IDs
    user1_score: Mapped[int] = mapped_column(Integer, default=0)
    user2_score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user1: Mapped["User"] = relationship(foreign_keys=[user1_id], back_populates="duels_as_user1")
    user2: Mapped["User"] = relationship(foreign_keys=[user2_id], back_populates="duels_as_user2")
    duel_answers: Mapped[List["DuelAnswer"]] = relationship(back_populates="duel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Duel(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id}, status={self.status})>"


class DuelAnswer(Base):
    """Answers during duel (guessing opponent's answers)"""
    __tablename__ = "duel_answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    duel_id: Mapped[int] = mapped_column(Integer, ForeignKey("duels.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    guessed_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    duel: Mapped["Duel"] = relationship(back_populates="duel_answers")
    user: Mapped["User"] = relationship(back_populates="duel_answers")
    question: Mapped["Question"] = relationship(back_populates="duel_answers")
    
    def __repr__(self):
        return f"<DuelAnswer(duel_id={self.duel_id}, user_id={self.user_id}, question_id={self.question_id})>"
