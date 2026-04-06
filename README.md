# Telegram Job Bot 📋🤖

## 🚀 Project Overview

This Telegram bot automates job updates, currency rates, and data delivery via Excel files.
It is designed to save time and provide users with up-to-date information daily.


Бот для автоматической отправки Excel-файла с ноутбуками и свежими вакансиями с сайта [remoteok.com](https://remoteok.com), а также отображения новостей и курса USD к AMD.

## 🚀 Возможности
- 📥 Получение Excel-файла с ноутбуками
- 💵 Актуальный курс USD к AMD
- 📢 Новости из мира технологий
- 📌 Последние вакансии с remoteok.com
- ⏰ Автоматическая отправка Excel и вакансий каждый день в 10:00

## 📦 Установка

```bash
git clone https://github.com/yourusername/telegram-job-bot.git
cd telegram-job-bot
pip install -r requirements.txt

## ⚙️ Использование

Создай файл `subscribers.json` (можно пустой: `[]`), затем запусти:

```bash
python bot.py



📱 Команды бота
/start — Главное меню

/subscribe — Подписаться на автоотправку

/unsubscribe — Отписаться от автоотправки

/autoparse — Получить Excel-файл вручную

/status — Проверить статус подписки

📁 Файлы
bot.py — основной код бота

parser.py — парсер ноутбуков

subscribers.json — список ID чатов с подпиской

🧑‍💻 Автор
Gev — начинающий Python-разработчик 🚀
