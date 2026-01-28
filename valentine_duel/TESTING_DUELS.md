# 🎮 Valentine Duel Bot - Testing Guide

## 🚀 Quick Start with Duel System

### 1️⃣ Recreate Database (if needed)
```bash
python recreate_db.py
```

### 2️⃣ Seed Questions
```bash
python seed_questions.py
```

### 3️⃣ Test Duel System
```bash
python test_duels.py
```

### 4️⃣ Run Bot
```bash
python main.py
```

---

## 🎯 Duel Mechanics Implementation

### ✅ Implemented Features

#### 1. **User Invitation & Matching**
- User1 enters opponent's @username
- Bot creates pending duel
- Generates personal invite link: `https://t.me/bot?start=duel_USER1`
- User1 forwards link to User2
- User2 clicks link, fills questionnaire, enters User1's username
- **MATCHING** happens automatically!

#### 2. **Deep Links Support**
- `/start duel_USERNAME` - processes invitation
- Stores inviter info during onboarding
- Shows invitation message after registration

#### 3. **Duel Gameplay**
- Both players click "🎯 Начать дуэль"
- Bot selects 5 random questions
- Players guess opponent's answers
- Progress tracking: "Вопрос 2 из 5"

#### 4. **Score Calculation**
- Compares guesses with real answers from questionnaire
- Awards points based on question weight
- Tracks correct/incorrect answers

#### 5. **Results & Prizes**
- Detailed statistics for both players
- Winner gets promo code
- Loser gets sticker pack
- "Новая дуэль" button for rematch

---

## 📋 Duel Status Flow

```
pending → matched → active → completed
   ↓         ↓         ↓         ↓
User1    User2    Both      Results
invites  accepts  playing   + Prizes
```

---

## 🧪 Testing Scenarios

### Scenario 1: Both Users in Bot
```
1. User1: "🎮 Новая дуэль" → enters @user2
2. User1: Gets invite link
3. User2: "🎮 Новая дуэль" → enters @user1
4. ✅ MATCHING! Both get "Начать дуэль" button
```

### Scenario 2: User2 Not in Bot
```
1. User1: "🎮 Новая дуэль" → enters @user2
2. User1: Gets invite link, forwards to User2
3. User2: Clicks link → /start duel_user1
4. User2: Completes registration + questionnaire
5. User2: "🎮 Новая дуэль" → enters @user1
6. ✅ MATCHING!
```

### Scenario 3: Full Duel Game
```
1. After matching, both click "🎯 Начать дуэль"
2. Bot selects 5 random questions
3. Each player answers 5 questions
4. Bot calculates scores
5. Both receive results + prizes
6. Option to play again
```

---

## 🔧 Database Schema Changes

### Updated `duels` table:
```python
user2_id: Optional[int]  # Now nullable for pending status
status: "pending" | "matched" | "active" | "completed"
selected_questions: List[int]  # JSON array of 5 question IDs
```

---

## 📁 New Files Created

- `/app/handlers/duel.py` - Full duel logic (500+ lines)
- `/app/keyboards/inline.py` - Updated with duel buttons
- `/test_duels.py` - Automated tests
- `/recreate_db.py` - DB schema migration
- `TESTING_DUELS.md` - This file

---

## 🐛 Known Limitations

1. **No APScheduler Reminders** (planned for v2)
2. **No Image Generation** for results sharing (planned for v2)
3. **Simple Matching Logic** - no notification if opponent offline

---

## 🎯 Next Steps for Production

1. ✅ Test matching with 2 real Telegram accounts
2. ✅ Test full duel gameplay
3. ✅ Verify prizes delivery
4. ⏳ Add APScheduler for reminders
5. ⏳ Add Pillow for result images
6. ⏳ Add analytics/logging

---

## 💡 Tips

- Use `/start` to reset and return to main menu
- Test with 2 different Telegram accounts
- Check logs for debugging
- Questions weight affects scoring!

---

## 🆘 Troubleshooting

### "Not enough questions"
```bash
python seed_questions.py
```

### "Database schema mismatch"
```bash
python recreate_db.py
python seed_questions.py
```

### "Import errors"
```bash
pip install -r requirements.txt
```

---

## ✨ Ready to Launch!

The core duel mechanics are **fully implemented** and ready for testing! 🚀

Запускайте и проверяйте матчинг! 💪
