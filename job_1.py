import requests
import pytz
import json
import os
import datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import InputFile, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update
from parser import parse_laptops  


SUBSCRIBERS_FILE = "subscribers.json"


def parse_jobs(limit=5):
    url = "https://remoteok.com/remote-dev+python-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.select("tr.job")  

        result = []
        for job in jobs:
            if "data-id" not in job.attrs:
                continue  

            title_tag = job.select_one("td.position h2")
            company_tag = job.select_one("td.company h3")
            link_tag = job.get("data-href")

            if not title_tag or not company_tag or not link_tag:
                continue

            title = title_tag.text.strip()
            company = company_tag.text.strip()
            link = "https://remoteok.com" + link_tag.strip()

            result.append(f"💼 {title} — {company}\n🔗 {link}")

            if len(result) >= limit:
                break

        return "\n\n".join(result) if result else "❌ Вакансии не найдены."

    except Exception as e:
        return f"❌ Ошибка при получении вакансий: {e}"


def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f)


from pytz import timezone  
armenia = timezone("Asia/Yerevan")
TOKEN = "7256527051:AAEgPdUZzLRLHtv3rz67qj7JW2SX1E8tD9M"
scheduler = BackgroundScheduler()
scheduler.start()
print("🚀 ПЛАНИРОВЩИК ЗАПУЩЕН")

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Excel", callback_data='get_excel'),
         InlineKeyboardButton("💵 Курс", callback_data='get_usd')],
        [InlineKeyboardButton("📢 Новости", callback_data='get_news')],
        [InlineKeyboardButton("🔁 Обновить", callback_data='refresh')],
        [InlineKeyboardButton("❌ Удалить", callback_data='delete')],
        [InlineKeyboardButton("📌 Вакансии", callback_data='get_jobs')]
    ])



def get_news(limit=5):
    url = "https://www.theverge.com/tech"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        news_list = []
        links = soup.find_all("a", href=True)

        for link in links:
            title = link.text.strip()
            href = link["href"]

            # фильтруем мусор
            if len(title) < 25 or "theverge.com" not in href and not href.startswith("/"):
                continue

            # делаем ссылку полной
            if not href.startswith("http"):
                href = "https://www.theverge.com" + href

            news_list.append(f"📰 {title}\n🔗 {href}")

            if len(news_list) >= limit:
                break

        return "\n\n".join(news_list) if news_list else "❌ Новости не найдены."

    except Exception as e:
        return f"❌ Ошибка при получении новостей: {e}"

    


def get_usd_to_amd():
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        print("Реальный ответ:", data)
        if "rates" in data and "AMD" in data["rates"]:
            return round(data["rates"]["AMD"], 2)
        else:
            return "Ошибка: курс не найден"
    except Exception as e:
        print("Ошибка запроса:", e)
        return "Ошибка соединения"


def start(update, context):
    
    update.message.reply_text("🔽 Выберите действие:", reply_markup=main_keyboard())

def subscribe(update, context):
    from pytz import timezone
    armenia = timezone("Asia/Yerevan")

    chat_id = update.message.chat_id
    print("✅ Задача добавлена для чата:", chat_id)

    # Загружаем текущее состояние
    subscribers = load_subscribers()

    # Сохраняем, если ещё не был подписан
    if chat_id not in subscribers:
        subscribers.append(chat_id)
        save_subscribers(subscribers)
        print("1sub")

    scheduler.add_job(
        scheduled_task,
        trigger='cron',
        hour=datetime.datetime.now().hour,
        minute=(datetime.datetime.now().minute + 1) % 60,
        args=[chat_id],
        id=str(chat_id),
        replace_existing=True,
        timezone=armenia
    )

    


    update.message.reply_text("✅ Автоотправка включена.")

def unsubscribe(update, context):
    chat_id = update.message.chat_id
    removed = False

    for task_id in [str(chat_id), f"{chat_id}_jobs"]:
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)
            removed = True
    
    subscribers = load_subscribers()
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)

    if removed:
        update.message.reply_text("❌ Автоотправка отключена.")
    else:
        update.message.reply_text("ℹ️ У тебя не было активных автоотправок.")


def autoparse(update, context):
    update.message.reply_text("⏳ Автопарсинг запущен...")
    parse_laptops("laptops_auto.xlsx")
    with open("laptops_auto.xlsx", "rb") as file:
        update.message.reply_document(document=InputFile(file), filename="АвтоНоутбуки.xlsx")



def status(update, context):
    chat_id = update.message.chat_id
    subscribers = load_subscribers()
    if chat_id in subscribers:
        update.message.reply_text("✅ Ты подписан на автообновления.")
    else:
        update.message.reply_text("ℹ️ Ты не подписан.")


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()


    

    if query.data == "get_excel":
        query.edit_message_text("⏳ Получаю Excel-файл...")
        parse_laptops("laptops_auto.xlsx")
        with open("laptops_auto.xlsx", "rb") as file:
            context.bot.send_document(chat_id=query.message.chat_id, document=InputFile(file), filename="Ноутбуки.xlsx")
      
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data='back')]
        ])
        context.bot.send_message(chat_id=query.message.chat_id, text="Готово. 🔽 Вернуться назад?", reply_markup=keyboard)

    elif query.data == "get_usd":
        rate = get_usd_to_amd()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data='back')]
        ])
        query.edit_message_text(f"💵 1 USD = {rate} AMD", reply_markup=keyboard)

    elif query.data == "get_news":
        query.edit_message_text("🔍 Получаю новости...")
        news = get_news()
        context.bot.send_message(chat_id=query.message.chat_id, text=news)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data='back')]
        ])
        context.bot.send_message(chat_id=query.message.chat_id, text="🔽 Вернуться назад?", reply_markup=keyboard)
        

    elif query.data == "refresh":
        query.edit_message_text("🔽 Обновлено! Выберите действие:", reply_markup=main_keyboard())


    elif query.data == "delete":
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    elif query.data == "back":
        query.edit_message_text("🔽 Главное меню:", reply_markup=main_keyboard())

    elif query.data == "get_jobs":
        query.edit_message_text("🔍 Ищу вакансии...")
        jobs = parse_jobs()
        context.bot.send_message(chat_id=query.message.chat_id, text=jobs)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data='back')]
        ])
        context.bot.send_message(chat_id=query.message.chat_id, text="🔽 Вернуться назад?", reply_markup=keyboard)


def scheduled_task(chat_id):
    print("✅ ЗАДАЧА СРАБОТАЛА для", chat_id)
    from telegram import Bot
    print("🟡 Задача сработала, создаю бот...")
    bot = Bot(TOKEN)
    parse_laptops("laptops_auto.xlsx")
    print("🟡 Парсинг завершён")

    try:
        with open("laptops_auto.xlsx", "rb") as file:
            print("📤 Отправляю файл...")
            bot.send_document(chat_id=chat_id, document=InputFile(file), filename="АвтоНоутбуки.xlsx")
            bot.send_message(chat_id=chat_id, text="🕒 Это автообновление. До завтра!")
    except Exception as e:
        print("❌ Ошибка при отправке:", e)

    jobs = parse_jobs()
    bot.send_message(chat_id=chat_id, text="🕒 Новые вакансии:\n\n" + jobs)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher


    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(CommandHandler("autoparse", autoparse))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dp.add_handler(CommandHandler("status", status))


    for chat_id in load_subscribers():
        scheduler.add_job(
            scheduled_task,
            trigger='cron',
            hour=10, minute=0,
            args=[chat_id],
            id=str(chat_id),
            replace_existing=True,
            timezone=armenia
        )
        print(f"🔁 Восстановлена задача для {chat_id}")


    updater.start_polling()
    updater.idle()



if __name__ == "__main__":
    main()

