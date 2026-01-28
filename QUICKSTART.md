# 🚀 БЫСТРЫЙ СТАРТ - Валентиновый дуэль

## ⚡ За 5 минут до запуска

### 1️⃣ Получите токен бота (2 минуты)

1. Откройте Telegram → найдите @BotFather
2. Отправьте `/newbot`
3. Назовите бота (например: Valentine Duel Bot)
4. Выберите username (например: valentine_duel_bot)
5. **Скопируйте токен** - он выглядит так: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2️⃣ Загрузите проект на GitHub (2 минуты)

```bash
# Распакуйте архив
tar -xzf valentine_duel_bot.tar.gz
cd valentine_duel

# Инициализируйте Git
git init
git add .
git commit -m "Initial commit"

# Создайте репозиторий на GitHub, затем:
git remote add origin https://github.com/ВАШ_USERNAME/valentine-duel-bot.git
git branch -M main
git push -u origin main
```

### 3️⃣ Локальный запуск (1 минута)

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или: venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте .env
cp .env.example .env
nano .env  # Вставьте ваш BOT_TOKEN

# Инициализируйте БД и вопросы
python seed_questions.py

# Запустите бота
python main.py
```

**Готово! Проверьте бота командой /start в Telegram**

---

## 🖥️ Развертывание на VPS (Ubuntu/Debian)

### Полная установка за 10 минут

```bash
# 1. Подключитесь к серверу
ssh user@your-server-ip

# 2. Установите зависимости
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib

# 3. Настройте PostgreSQL
sudo -u postgres psql << EOF
CREATE DATABASE valentine_duel;
CREATE USER valentine_user WITH PASSWORD 'ваш_пароль';
GRANT ALL PRIVILEGES ON DATABASE valentine_duel TO valentine_user;
\q
EOF

# 4. Клонируйте репозиторий
sudo mkdir -p /opt/valentine-duel-bot
sudo chown $USER:$USER /opt/valentine-duel-bot
cd /opt/valentine-duel-bot
git clone https://github.com/ВАШ_USERNAME/valentine-duel-bot.git .

# 5. Установите Python зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Настройте .env
cp .env.example .env
nano .env
```

**В .env укажите:**
```env
BOT_TOKEN=ваш_токен_от_BotFather
DATABASE_URL=postgresql+asyncpg://valentine_user:ваш_пароль@localhost:5432/valentine_duel
ADMIN_PASSWORD=придумайте_пароль
ADMIN_SECRET_KEY=случайная_строка
```

```bash
# 7. Инициализируйте базу
python seed_questions.py

# 8. Создайте systemd сервис
sudo tee /etc/systemd/system/valentine-duel-bot.service > /dev/null << EOF
[Unit]
Description=Valentine Duel Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/valentine-duel-bot
Environment="PATH=/opt/valentine-duel-bot/venv/bin"
ExecStart=/opt/valentine-duel-bot/venv/bin/python /opt/valentine-duel-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 9. Запустите бота
sudo systemctl daemon-reload
sudo systemctl enable valentine-duel-bot
sudo systemctl start valentine-duel-bot

# 10. Проверьте статус
sudo systemctl status valentine-duel-bot
```

---

## 🐳 Docker (самый простой способ)

```bash
# 1. Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin

# 2. Клонируйте проект
git clone https://github.com/ВАШ_USERNAME/valentine-duel-bot.git
cd valentine-duel-bot

# 3. Настройте .env
cp .env.example .env
nano .env  # Укажите BOT_TOKEN

# 4. Запустите
docker compose up -d

# 5. Инициализируйте БД
docker compose exec bot python seed_questions.py

# Готово! Проверьте логи:
docker compose logs -f bot
```

---

## 📋 Управление ботом

### Команды для systemd:

```bash
# Просмотр логов
sudo journalctl -u valentine-duel-bot -f

# Перезапуск
sudo systemctl restart valentine-duel-bot

# Остановка
sudo systemctl stop valentine-duel-bot

# Статус
sudo systemctl status valentine-duel-bot
```

### Команды для Docker:

```bash
# Просмотр логов
docker compose logs -f bot

# Перезапуск
docker compose restart

# Остановка
docker compose stop

# Статус
docker compose ps
```

---

## 🔄 Обновление после изменений

### Systemd:
```bash
cd /opt/valentine-duel-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart valentine-duel-bot
```

### Docker:
```bash
cd valentine-duel-bot
git pull origin main
docker compose down
docker compose up -d --build
```

---

## ✅ Чек-лист готовности

- [x] Проект создан и работает локально
- [ ] Получен токен от @BotFather
- [ ] Код загружен на GitHub
- [ ] Сервер настроен (VPS или Docker)
- [ ] База данных создана
- [ ] .env файл настроен
- [ ] Бот запущен и отвечает на /start
- [ ] Логи проверены - нет ошибок

---

## 🆘 Если что-то не работает

### Бот не отвечает:
```bash
# Проверьте логи
sudo journalctl -u valentine-duel-bot -n 50
# или
docker compose logs bot --tail 50

# Проверьте .env
cat .env | grep BOT_TOKEN
```

### Ошибка БД:
```bash
# Проверьте PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"
```

### Ошибка зависимостей:
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 📞 Поддержка

- 📖 Полная документация: `README.md`
- 🚀 Деплой инструкция: `DEPLOYMENT.md`
- 🐛 Проблемы: создайте Issue на GitHub

---

**Удачи с запуском! К 14 февраля всё будет готово! 💑🎮**
