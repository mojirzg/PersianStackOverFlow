from telegram.ext import *
from telegram import *
import logging
import config
import database as db
import conversation as cn
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# region menu


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def callback(bot, update):
    print(update.callback_query)
    a_text = update.callback_query.message.text
    x = a_text.index(']')
    sender_id = a_text[6:x]
    print(sender_id)
    if update.callback_query.data == "like":
        print('liked')
        db.change('addlike', sender_id, None)
    elif update.callback_query.data == "dislike":
        print('disliked')  # todo show another answer
    elif update.callback_query.data == "report":
        print('report')
    elif update.callback_query.data == "Qreport":
        print('Qreport')
        if db.change('report', db.question_by_id(sender_id), None) > 5:
            db.change('ban', db.get(db.question_by_id(sender_id)), False)
    elif update.callback_query.data == "reply":
        bot.answer_callback_query(update.callback_query.id, text="پاسخ خود را به صورت ریپلی سوال بفرستید...",
                                  show_alert=True)


# endregion


def start(bot, update):
    update.message.reply_text('متن خوش آمد گویی')
    print(update.message.chat_id)
    chatid = update.message.chat_id
    if db.get_username(chatid):
        a = db.db['info'].find_one(chatid=update.message.chat_id)
        if a['status'] == 1:
            reply_keyboard = [['/ask']]
            update.message.reply_text('برای پرسیدن سوال /ask را ارسال کنید',
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                       resize_keyboard=True))
            pass
        else:
            reply_keyboard = [['/user']]
            update.message.reply_text('ثبت نام شما کامل نیست لطفا با دستور /user مجددا ثبت نام کنید',
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
    else:
        reply_keyboard = [['/user']]
        update.message.reply_text('یوزر را ارسال کنید /user',
                                  reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))


def help(bot, update):
    db.droptable()
    print("info table dropped")
    update.message.reply_text("info table dropped")


def answer(bot, update):
    button_list = [
        InlineKeyboardButton("👎🏻   " + 'کمکی نکرد', callback_data="dislike"),
        InlineKeyboardButton("👍🏻   " + 'کمک کرد', callback_data="like"),
        InlineKeyboardButton("⛔️   " + 'ریپورت', callback_data="report"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    q_text = update.message.reply_to_message.text  # text of the question
    text = 'sender_id : [' + str(update.message.chat_id) + ']' + '\n\n' + update.message.text
    if 'sender_id' in q_text:
        x = q_text.index(']')
        bot.send_message(chat_id=db.question_by_id(q_text[6:x]), text=text,
                         reply_markup=reply_markup)

        bot.send_message(chat_id=config.channel_id,
                         reply_to_message_id=db.get(db.question_by_id(q_text[6:x]))['channel_msgid'],
                         text=update.message.text)

        # send the answer


def data(bot, update):
    y = datetime.datetime.now()
    print(y)
    x = datetime.datetime.now()
    print(x)
    print(x - y)
    if x - y > datetime.timedelta(minutes=1):
        print("ok, 60 seconds have passed")


def channel_handler(bot, update):
    print(update.channel_post.text)


def text(bot, update):
    update.message.reply_text(str(update.message.text))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config.token)

    db.database_info()

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
    # dp.add_handler(MessageHandler(Filters.chat(int(config.channel_id)), channel_handler,
    #                              channel_post_updates=True))
    # dp.add_handler(CallbackQueryHandler(callback=callback))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
