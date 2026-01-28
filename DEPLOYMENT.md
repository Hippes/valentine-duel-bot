# 🚀 Руководство по загрузке проекта в GitHub и развертыванию

## 📥 Шаг 1: Загрузка проекта в GitHub

### 1.1. Создайте новый репозиторий на GitHub

1. Перейдите на https://github.com
2. Нажмите "+" в правом верхнем углу → "New repository"
3. Название: `valentine-duel-bot`
4. Описание: `Interactive Telegram bot for couples games`
5. Выберите: **Private** (если хотите скрыть токены) или **Public**
6. НЕ добавляйте README, .gitignore, license (они уже есть в проекте)
7. Нажмите "Create repository"

### 1.2. Инициализируйте Git локально

```bash
# Перейдите в директорию проекта
cd valentine_duel

# Инициализируйте Git
git init

# Добавьте все файлы
git add .

# Сделайте первый коммит
git commit -m "Initial commit: Valentine Duel Bot"

# Добавьте удаленный репозиторий (замените YOUR_USERNAME на ваш username)
git remote add origin https://github.com/YOUR_USERNAME/valentine-duel-bot.git

# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

### 1.3. Проверка

Обновите страницу вашего репозитория на GitHub - вы должны увидеть все файлы проекта.

## 🔐 Шаг 2: Настройка секретов для GitHub Actions (опционально)

Если вы планируете использовать GitHub Actions для автоматического деплоя:

1. Перейдите в Settings → Secrets and variables → Actions
2. Нажмите "New repository secret"
3. Добавьте секреты:
   - `BOT_TOKEN` - токен вашего Telegram бота
   - `SERVER_HOST` - IP адрес вашего сервера
   - `SERVER_USER` - пользователь для SSH
   - `SERVER_SSH_KEY` - приватный SSH ключ

## 💻 Шаг 3: Развертывание на сервере

### Вариант A: Ручное развертывание на VPS

#### 3.1. Подключитесь к серверу

```bash
ssh your_user@your_server_ip
```

#### 3.2. Установите необходимые пакеты

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите зависимости
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib
```

#### 3.3. Настройте PostgreSQL

```bash
# Войдите в PostgreSQL
sudo -u postgres psql

# Выполните SQL команды:
CREATE DATABASE valentine_duel;
CREATE USER valentine_user WITH PASSWORD 'your_strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE valentine_duel TO valentine_user;
\q
```

#### 3.4. Клонируйте репозиторий

```bash
# Создайте директорию
sudo mkdir -p /opt/valentine-duel-bot
sudo chown $USER:$USER /opt/valentine-duel-bot
cd /opt/valentine-duel-bot

# Клонируйте проект
git clone https://github.com/YOUR_USERNAME/valentine-duel-bot.git .
```

#### 3.5. Настройте окружение

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp .env.example .env
nano .env
```

Отредактируйте `.env`:
```env
BOT_TOKEN=ваш_токен_от_BotFather
DATABASE_URL=postgresql+asyncpg://valentine_user:your_strong_password_here@localhost:5432/valentine_duel
ADMIN_PASSWORD=your_admin_password
ADMIN_SECRET_KEY=generate_random_key_here
PROMO_CODE=SALE20%
STICKER_PACK_URL=https://t.me/addstickers/your_pack
```

#### 3.6. Инициализируйте базу данных

```bash
python seed_questions.py
```

#### 3.7. Создайте systemd сервис

```bash
sudo nano /etc/systemd/system/valentine-duel-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Valentine Duel Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/valentine-duel-bot
Environment="PATH=/opt/valentine-duel-bot/venv/bin"
ExecStart=/opt/valentine-duel-bot/venv/bin/python /opt/valentine-duel-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Замените `YOUR_USERNAME` на ваше имя пользователя.

#### 3.8. Запустите бота

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable valentine-duel-bot

# Запустите сервис
sudo systemctl start valentine-duel-bot

# Проверьте статус
sudo systemctl status valentine-duel-bot
```

#### 3.9. Проверка логов

```bash
# Просмотр логов в реальном времени
sudo journalctl -u valentine-duel-bot -f

# Последние 50 строк логов
sudo journalctl -u valentine-duel-bot -n 50
```

### Вариант B: Развертывание через Docker

#### 3.1. Установите Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose-plugin

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

#### 3.2. Клонируйте проект

```bash
git clone https://github.com/YOUR_USERNAME/valentine-duel-bot.git
cd valentine-duel-bot
```

#### 3.3. Настройте .env

```bash
cp .env.example .env
nano .env
```

Отредактируйте параметры (BOT_TOKEN и др.)

**Важно:** Для Docker используйте:
```env
DATABASE_URL=postgresql+asyncpg://valentine_user:change_this_password@db:5432/valentine_duel
```

#### 3.4. Запустите контейнеры

```bash
# Запуск
docker compose up -d

# Инициализация БД
docker compose exec bot python seed_questions.py

# Просмотр логов
docker compose logs -f bot
```

#### 3.5. Управление контейнерами

```bash
# Остановка
docker compose stop

# Перезапуск
docker compose restart

# Просмотр статуса
docker compose ps

# Обновление после изменений
git pull
docker compose down
docker compose up -d --build
```

## 🔄 Обновление бота на сервере

### Для systemd:

```bash
cd /opt/valentine-duel-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart valentine-duel-bot
```

### Для Docker:

```bash
cd /path/to/valentine-duel-bot
git pull origin main
docker compose down
docker compose up -d --build
```

## 📊 Мониторинг

### Проверка работоспособности

```bash
# Для systemd
sudo systemctl status valentine-duel-bot

# Для Docker
docker compose ps
docker compose logs bot --tail 100
```

### Просмотр логов

```bash
# Для systemd
sudo journalctl -u valentine-duel-bot -f

# Для Docker
docker compose logs -f bot
```

## 🐛 Решение проблем

### Бот не запускается

1. **Проверьте токен:**
```bash
cat .env | grep BOT_TOKEN
```

2. **Проверьте логи:**
```bash
sudo journalctl -u valentine-duel-bot -n 100
# или
docker compose logs bot --tail 100
```

3. **Проверьте подключение к БД:**
```bash
# Для systemd
sudo -u postgres psql -c "\l"

# Для Docker
docker compose exec db psql -U valentine_user -d valentine_duel -c "SELECT 1;"
```

### База данных не работает

```bash
# Проверьте статус PostgreSQL
sudo systemctl status postgresql

# Перезапустите PostgreSQL
sudo systemctl restart postgresql
```

### Ошибки зависимостей

```bash
# Переустановите зависимости
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 🔐 Безопасность

### Рекомендации:

1. **Никогда не коммитьте .env файл**
   - Он уже в .gitignore, но всегда проверяйте

2. **Используйте сильные пароли**
   - Для PostgreSQL
   - Для админ-панели

3. **Настройте firewall**
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (если будет админка)
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

4. **Регулярно обновляйте систему**
```bash
sudo apt update && sudo apt upgrade -y
```

## ✅ Чек-лист перед запуском

- [ ] Создан бот через @BotFather и получен токен
- [ ] Репозиторий создан на GitHub
- [ ] Код загружен в GitHub
- [ ] Сервер настроен (VPS или Docker)
- [ ] PostgreSQL установлена и настроена
- [ ] Файл .env создан и заполнен
- [ ] База данных инициализирована (seed_questions.py)
- [ ] Systemd сервис создан и запущен (или Docker контейнеры)
- [ ] Бот отвечает на команду /start
- [ ] Логи проверены и не содержат ошибок

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте README.md
2. Проверьте логи
3. Создайте Issue в GitHub репозитории

---

**Удачного запуска! 🚀**
