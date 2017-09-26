from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
# import config
import database as db
import conversation as CN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('متن خوش آمد گویی')
    chatid = update.message.chat_id
    if db.UserName.get_username(chatid):
        print(db.UserName.get_username(chatid))
        update.message.reply_text('سوال خود را بپرسید')
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


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('457322349:AAGX7G-k9uyErrDO2CoBi4qKeC3FRe2zJS4')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    # region conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('user', CN.start)],

        states={
            CN.flag_yes: [RegexHandler('^(بله)$', CN.flag_yes),
                          RegexHandler('^(خیر)$', CN.flag_no)],

            CN.lan: [RegexHandler('^(Python|Photoshop|C#)$', CN.lan),
                     CommandHandler('Done', CN.lan_done),
                     CommandHandler('Cancel', CN.lan_cancel)],

            CN.lan_done: [RegexHandler('^(خیر)$', CN.lan),
                          RegexHandler('^(بله)$', CN.check)],

        },

        fallbacks=[CommandHandler('cancel', CN.cancel)]
    )

    dp.add_handler(conv_handler)
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
