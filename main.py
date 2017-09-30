from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import config
import database as db
import conversation as cn
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('متن خوش آمد گویی')
    chatid = update.message.chat_id
    if db.get_username(chatid):
        reply_keyboard = [['/ask']]
        print(db.get_username(chatid))
        update.message.reply_text('ّبرای پرسیدن سوال /ask را ارسال کنید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        pass
    else:
        reply_keyboard = [['/user']]
        update.message.reply_text('یوزر را ارسال کنید /user',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))


def help(bot, update):
    db.droptable()
    print("info table dropped")
    update.message.reply_text("info table dropped")


def answer(bot, update):
    q_text = update.message.reply_to_message.text  # text of the question
    if 'ID' in q_text:
        x = q_text.index(']')
        bot.send_message(chat_id=db.question_by_id(q_text[6:x]), text=update.message.text)
        # send the answer


def data(bot, update):
    y = datetime.datetime.now()
    print(y)
    x = datetime.datetime.now()
    print(x)
    print(x - y)
    if x - y > datetime.timedelta(minutes=1):
        print("ok, 60 seconds have passed")


def text(bot, update):
    update.message.reply_text(str(update.message.text))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config.token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("d", data))  # for test purposes

    # region conversation handler
    dp.add_handler(cn.conv_handler_question)
    dp.add_handler(cn.conv_handler)
    # endregion

    dp.add_handler(MessageHandler(Filters.reply, answer))  # for answers
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
