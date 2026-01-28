"""
Script to seed initial questions into database
"""
import asyncio
from app.database import async_session_maker, Question


QUESTIONS_DATA = [
    {
        "text": "Любимая еда перед сном:",
        "options": {
            "options": [
                "Паста",
                "Роллы",
                "Чай с печеньками",
                "Рулька",
                "Ничего.. уже после 6 часов"
            ]
        },
        "weight": 1
    },
    {
        "text": "Любимый жанр кино/сериалов:",
        "options": {
            "options": [
                "Детектив",
                "Нон-фикшн",
                "Бизнес чтиво",
                "Фэнтези",
                "Классика",
                "Ничего из списка"
            ]
        },
        "weight": 1
    },
    {
        "text": "Любимое время года:",
        "options": {
            "options": [
                "Зима",
                "Весна",
                "Лето",
                "Осень"
            ]
        },
        "weight": 1
    },
    {
        "text": "Любимая среда обитания:",
        "options": {
            "options": [
                "Пляж",
                "Океан",
                "Море",
                "Пустыня",
                "Джунгли",
                "Тайга",
                "Городской ландшафт",
                "Там, где снег"
            ]
        },
        "weight": 1
    },
    {
        "text": "Любимый тип блюда:",
        "options": {
            "options": [
                "Суп-пюре",
                "Салатик",
                "Жаркое",
                "Стейк",
                "Закуска",
                "Десерт",
                "Блюда на компанию"
            ]
        },
        "weight": 1
    },
    {
        "text": "Начало дня:",
        "options": {
            "options": [
                "Кто я?",
                "А почему все спят?",
                "Кто придумал будильники?",
                "Срочно поесть!",
                "Я еще не ложился"
            ]
        },
        "weight": 1
    },
    {
        "text": "Тип музыки:",
        "options": {
            "options": [
                "Поп",
                "Рок",
                "Металл",
                "Классика",
                "Регги",
                "Музыка без слов"
            ]
        },
        "weight": 1
    },
    {
        "text": "Какая профессия подходит:",
        "options": {
            "options": [
                "Музыкант",
                "Художник",
                "Банкир",
                "Политик",
                "Космонавт",
                "Тестировщик кроватей"
            ]
        },
        "weight": 1
    },
    {
        "text": "Что покажешь в игре КНБ первым:",
        "options": {
            "options": [
                "Камень",
                "Ножницы",
                "Бумага",
                "Колодец",
                "Труба",
                "Огонь"
            ]
        },
        "weight": 1
    },
    {
        "text": "Что ближе по духу:",
        "options": {
            "options": [
                "Гуманитарий",
                "Технический"
            ]
        },
        "weight": 1
    }
]


async def seed_questions():
    """Seed initial questions into database"""
    async with async_session_maker() as session:
        # Check if questions already exist
        from sqlalchemy import select
        result = await session.execute(select(Question))
        existing = result.scalars().first()
        
        if existing:
            print("Questions already exist in database. Skipping seed.")
            return
        
        # Add questions
        for q_data in QUESTIONS_DATA:
            question = Question(
                text=q_data["text"],
                options=q_data["options"],
                weight=q_data["weight"],
                is_active=True
            )
            session.add(question)
        
        await session.commit()
        print(f"Successfully seeded {len(QUESTIONS_DATA)} questions!")


if __name__ == "__main__":
    asyncio.run(seed_questions())
