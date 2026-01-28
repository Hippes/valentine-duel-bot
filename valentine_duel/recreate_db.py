#!/usr/bin/env python3
"""
Recreate database with updated schema
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.models import Base
from config.settings import settings


async def recreate_database():
    """Drop and recreate all tables"""
    print("⚠️  WARNING: This will DELETE all data in the database!")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("❌ Cancelled")
        return
    
    print("\n🗑️  Dropping all tables...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("✅ All tables dropped")
    
    print("\n📊 Creating new tables with updated schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database recreated successfully!")
    print("\n💡 Don't forget to:")
    print("   1. Run: python seed_questions.py")
    print("   2. Test bot with: python main.py")
    
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(recreate_database())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
