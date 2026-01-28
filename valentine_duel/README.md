# 💑 Валентиновый дуэль - Telegram Bot

Интерактивный Telegram-бот для парных игр, где пользователи проверяют, насколько хорошо они знают предпочтения друг друга.

## 📋 Оглавление

- [Возможности](#возможности)
- [Технологический стек](#технологический-стек)
- [Установка и запуск](#установка-и-запуск)
- [Настройка](#настройка)
- [Деплой на сервер](#деплой-на-сервер)
- [Структура проекта](#структура-проекта)

## 🎯 Возможности

- ✅ Регистрация с согласием на политику конфиденциальности
- 📝 Персонализированный опросник из 10 вопросов
- 🎮 Парные дуэли с угадыванием ответов соперника
- 🏆 Система баллов с весовыми коэффициентами
- 🎁 Призы для победителей (промокоды) и проигравших (стикерпак)
- 📤 Шеринг результатов
- ⏰ Ремайндеры через 3 минуты бездействия
- 📊 Статистика дуэлей
- 🔄 Возможность повторных игр

## 🛠 Технологический стек

- **Python 3.10+**
- **aiogram 3.7** - асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** / SQLite - база данных
- **APScheduler** - планировщик задач для ремайндеров
- **Pillow** - генерация изображений результатов
- **Flask-Admin** - админ-панель (опционально)

## 📦 Установка и запуск

### Локальный запуск

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/valentine-duel-bot.git
cd valentine-duel-bot
```

2. **Создайте виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate  # Для Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл, добавьте ваш BOT_TOKEN
```

5. **Инициализируйте базу данных и добавьте вопросы:**
```bash
python seed_questions.py
```

6. **Запустите бота:**
```bash
python main.py
```

## ⚙️ Настройка

### Получение токена бота

1. Откройте Telegram и найдите бота [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям и получите токен
4. Добавьте токен в файл `.env`:
```
BOT_TOKEN=your_bot_token_here
```

### Настройка базы данных

#### SQLite (для разработки)
```env
DATABASE_URL=sqlite+aiosqlite:///./valentine_duel.db
```

#### PostgreSQL (для продакшена)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/valentine_duel
```

### Настройка призов

Отредактируйте `.env`:
```env
PROMO_CODE=SALE20%
STICKER_PACK_URL=https://t.me/addstickers/your_sticker_pack
```

## 🚀 Деплой на сервер

### Вариант 1: VPS (Ubuntu/Debian)

#### 1. Подготовка сервера

```bash
# Подключитесь к серверу
ssh user@your-server-ip

# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python и зависимости
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib git -y
```

#### 2. Установка PostgreSQL

```bash
# Войдите в PostgreSQL
sudo -u postgres psql

# Создайте базу данных и пользователя
CREATE DATABASE valentine_duel;
CREATE USER valentine_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE valentine_duel TO valentine_user;
\q
```

#### 3. Клонирование и настройка проекта

```bash
# Создайте директорию для проекта
cd /opt
sudo mkdir valentine-duel-bot
sudo chown $USER:$USER valentine-duel-bot
cd valentine-duel-bot

# Клонируйте репозиторий
git clone https://github.com/yourusername/valentine-duel-bot.git .

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Настройте .env
cp .env.example .env
nano .env  # Отредактируйте файл
```

#### 4. Инициализация базы данных

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите скрипт инициализации
python seed_questions.py
```

#### 5. Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/valentine-duel-bot.service
```

Добавьте:
```ini
[Unit]
Description=Valentine Duel Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/opt/valentine-duel-bot
Environment="PATH=/opt/valentine-duel-bot/venv/bin"
ExecStart=/opt/valentine-duel-bot/venv/bin/python /opt/valentine-duel-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6. Запуск сервиса

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Запустите бота
sudo systemctl start valentine-duel-bot

# Включите автозапуск
sudo systemctl enable valentine-duel-bot

# Проверьте статус
sudo systemctl status valentine-duel-bot

# Просмотр логов
sudo journalctl -u valentine-duel-bot -f
```

### Вариант 2: Docker

#### 1. Создайте Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### 2. Создайте docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: valentine_duel
      POSTGRES_USER: valentine_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3. Запуск

```bash
# Запустите контейнеры
docker-compose up -d

# Инициализируйте базу данных
docker-compose exec bot python seed_questions.py

# Просмотр логов
docker-compose logs -f bot
```

### Вариант 3: Heroku

#### 1. Установите Heroku CLI

```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Создайте Procfile

```
worker: python main.py
```

#### 3. Деплой

```bash
# Войдите в Heroku
heroku login

# Создайте приложение
heroku create valentine-duel-bot

# Добавьте PostgreSQL
heroku addons:create heroku-postgresql:mini

# Установите переменные окружения
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set PROMO_CODE=SALE20%
heroku config:set STICKER_PACK_URL=https://t.me/addstickers/your_pack

# Деплой
git push heroku main

# Инициализируйте базу данных
heroku run python seed_questions.py

# Включите worker
heroku ps:scale worker=1

# Просмотр логов
heroku logs --tail
```

## 📁 Структура проекта

```
valentine_duel/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy модели
│   │   └── database.py         # Подключение к БД
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py            # Обработчик /start
│   │   ├── questionnaire.py    # Опросник
│   │   └── duel.py            # Дуэли (TODO)
│   ├── keyboards/
│   │   └── inline.py          # Inline-клавиатуры
│   ├── middlewares/
│   │   └── db.py              # Middleware для БД сессий
│   └── utils/
│       ├── states.py           # FSM состояния
│       └── db_operations.py    # Операции с БД
├── config/
│   └── settings.py             # Настройки приложения
├── static/
│   ├── images/                 # Генерируемые изображения
│   └── templates/              # Шаблоны
├── admin/                      # Админ-панель (TODO)
├── .env.example                # Пример переменных окружения
├── .gitignore
├── requirements.txt            # Зависимости Python
├── seed_questions.py           # Скрипт инициализации вопросов
├── main.py                     # Точка входа
└── README.md                   # Документация
```

## 🔧 Управление ботом на сервере

### Команды systemd

```bash
# Запуск
sudo systemctl start valentine-duel-bot

# Остановка
sudo systemctl stop valentine-duel-bot

# Перезапуск
sudo systemctl restart valentine-duel-bot

# Статус
sudo systemctl status valentine-duel-bot

# Логи
sudo journalctl -u valentine-duel-bot -f
```

### Обновление бота

```bash
cd /opt/valentine-duel-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart valentine-duel-bot
```

## 🐛 Troubleshooting

### Проблема: Бот не запускается

**Решение:**
```bash
# Проверьте логи
sudo journalctl -u valentine-duel-bot -n 50

# Проверьте .env файл
cat .env

# Проверьте права доступа
ls -la /opt/valentine-duel-bot
```

### Проблема: Ошибка подключения к БД

**Решение:**
```bash
# Проверьте работу PostgreSQL
sudo systemctl status postgresql

# Проверьте строку подключения в .env
# Убедитесь, что пользователь и база данных существуют
sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "\du"
```

### Проблема: Бот не отвечает на команды

**Решение:**
- Проверьте токен бота в .env
- Убедитесь, что бот запущен: `sudo systemctl status valentine-duel-bot`
- Проверьте интернет-соединение сервера

## 📊 Мониторинг

### Просмотр логов в реальном времени

```bash
# Все логи
sudo journalctl -u valentine-duel-bot -f

# Последние 100 строк
sudo journalctl -u valentine-duel-bot -n 100

# Логи за сегодня
sudo journalctl -u valentine-duel-bot --since today
```

## 🔒 Безопасность

- ✅ Никогда не коммитьте .env файл в Git
- ✅ Используйте сильные пароли для БД
- ✅ Ограничьте доступ к серверу через firewall
- ✅ Регулярно обновляйте зависимости: `pip list --outdated`
- ✅ Используйте HTTPS для админ-панели

## 📝 TODO

- [ ] Реализовать полную механику дуэлей
- [ ] Добавить генерацию изображений результатов
- [ ] Реализовать ремайндеры через APScheduler
- [ ] Добавить админ-панель
- [ ] Добавить статистику пользователей
- [ ] Реализовать шеринг результатов

## 📄 Лицензия

MIT License - see LICENSE file for details

## 👨‍💻 Автор

Проект разработан для запуска к 14 февраля 2026 года.

## 🙏 Поддержка

Если у вас возникли проблемы, создайте Issue в репозитории.
