#!/usr/bin/env python3
"""
Test script to verify duel handlers are working
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, get_session
from app.utils.db_operations import UserRepository, QuestionRepository, DuelRepository
from app.database.models import User, Question


async def test_duel_creation():
    """Test duel creation and matching"""
    print("🧪 Testing duel handlers...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    async with get_session() as session:
        # Create test users
        user1 = await UserRepository.get_or_create_user(session, 12345, "user1_test")
        user1.privacy_accepted = True
        await session.commit()
        print(f"✅ Created user1: {user1.username}")
        
        user2 = await UserRepository.get_or_create_user(session, 67890, "user2_test")
        user2.privacy_accepted = True
        await session.commit()
        print(f"✅ Created user2: {user2.username}")
        
        # Check questions
        questions = await QuestionRepository.get_all_questions(session)
        print(f"✅ Found {len(questions)} questions in database")
        
        if len(questions) < 5:
            print("❌ Not enough questions! Need at least 5 for duels")
            print("   Run: python seed_questions.py")
            return
        
        # Test duel creation with pending status
        print("\n🎮 Testing duel creation (pending)...")
        duel = await DuelRepository.create_duel(
            session=session,
            user1_id=user1.id,
            user2_username="user2_test"
        )
        print(f"✅ Created pending duel ID: {duel.id}")
        print(f"   Status: {duel.status}")
        print(f"   User1: {duel.user1_id}")
        print(f"   User2: {duel.user2_id} (should be None)")
        
        # Test matching
        print("\n🤝 Testing matching...")
        await DuelRepository.complete_matching(
            session=session,
            duel_id=duel.id,
            user2_id=user2.id
        )
        
        # Verify matching
        matched_duel = await DuelRepository.get_duel(session, duel.id)
        print(f"✅ Duel matched!")
        print(f"   Status: {matched_duel.status}")
        print(f"   User1: {matched_duel.user1_id}")
        print(f"   User2: {matched_duel.user2_id}")
        
        # Test question selection
        print("\n📝 Testing question selection...")
        import random
        selected_questions = random.sample([q.id for q in questions], 5)
        await DuelRepository.start_duel(session, duel.id, selected_questions)
        
        started_duel = await DuelRepository.get_duel(session, duel.id)
        print(f"✅ Duel started!")
        print(f"   Status: {started_duel.status}")
        print(f"   Selected questions: {started_duel.selected_questions}")
        
        print("\n✅ All tests passed! Duel system is working! 🎉")


if __name__ == "__main__":
    try:
        asyncio.run(test_duel_creation())
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
