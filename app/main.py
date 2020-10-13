import os
import pytz

from datetime import datetime, timedelta
from telegram.ext import Dispatcher
from app import db
from app.models import Users, Ledger
import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re


API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    return now


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def ledger_handler(guarantors, amount, chat_id):
    all_users = Users.query.all()
    usernames = [user.username for user in all_users]
    # print(usernames)
    amount = float(amount) / len(guarantors)

    for i in guarantors:
        if i not in usernames:
            raise ValueError(f'Имя {i} отстуствует в таблице пользователей!')

    for guarantor in guarantors:
        user = Users.query.filter_by(username=guarantor).first()
        date = _get_now_datetime()
        sender = chat_id
        is_paid = True if user.telegram_id == chat_id else False
        balance = user.balance + amount * (len(guarantors)-1) if is_paid == True else user.balance - amount

        ledger = Ledger(sender=sender, guarantor=user.telegram_id, is_paid=is_paid, date=date,
                        amount=amount)
        db.session.add(ledger)
        user.balance = balance

    db.session.commit()
    #     print(user.telegram_id)
    # print(chat_id)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def balance(update, context):
    chat_id = update.message.chat_id
    user = Users.query.filter_by(telegram_id=chat_id).first()
    update.message.reply_text(f'Ваш баланс = {user.balance}')

def month(update, context):
    pass
    # chat_id = update.message.chat_id
    # month_raw = _get_now_datetime()
    # month = datetime(datetime.today().year, datetime.today().month, 8)
    # filter_date = datetime(datetime.today().year, datetime.today().month,1)
    # filtered = Ledger.query.filter(Ledger.sender==chat_id,Ledger.date>=filter_date).all()
    # # answer = ''
    # temp =[]
    # for i in filtered:
    #     temp.append(f'{i.sender} {i.guarantor} {i.amount} {i.date} \n')
    #     print(i.date, i.sender, i.amount)
    # update.message.reply_text(str(temp))
    # result = Ledger.query.filter_by(sender=198424525).first()
    # delta = timedelta(datet)
    # print(type(result.date))
    # print(result.date)
    # print(result.date - datetime.today())
    # print(type(result.date - datetime.today()))
    # print(type(datetime.today()-result.date))
    # print(datetime.today()-result.date)
    # print(type(month))

def add_payment(update, context):
    """Add payment to db"""
    msg_raw = update.message.text
    msg = msg_raw.split()
    ammount = msg[0]
    guarantors = msg[1]
    chat_id = update.message.chat_id
    try:
        ledger_handler(guarantors, ammount, chat_id)
    except ValueError as e:
        update.message.reply_text('*'*5 + str(e) + '*'*5)
        raise ValueError(str(e))
    update.message.reply_text("Запись успешно добавлена в таблицу.")
    print("Запись успешно добавлена в таблицу.")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(API_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    # dp.add_handler(CommandHandler("month", month))
    dp.add_handler(CommandHandler("balance", balance))
    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r'^(\d{1,6})\s(\D{1,4})'),
                                  add_payment))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()