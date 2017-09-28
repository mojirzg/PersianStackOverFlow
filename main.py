from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import config
import database as db
import conversation as cn

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


def data(bot, update):
    print(db.get(update.message.chat_id))


def text(bot, update):
    update.message.reply_text(update.message.text)

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
    dp.add_handler(CommandHandler("d", data))
    #dp.add_handler(MessageHandler(Filters.text, text))
    # region conversation handler
    dp.add_handler(cn.conv_handler_question)
    dp.add_handler(cn.conv_handler)
    # endregion
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
