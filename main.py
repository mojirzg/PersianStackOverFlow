from telegram.ext import *
from telegram import *
import logging
import config
import database as db
import conversation as cn
import datetime
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# region callback


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def callback(bot, update):
    a_text = update.callback_query.message.text
    x = a_text.index(']')
    sender_id = a_text[6:x]
    if update.callback_query.data == "like":
        if db.likes('get', update.callback_query.from_user.id, update.callback_query.message.message_id) is None:
            db.change('addlike', sender_id, None)
            db.likes('add', update.callback_query.from_user.id, update.callback_query.message.message_id)
        else:
            db.change('removelike', sender_id, None)
            db.likes('remove', update.callback_query.from_user.id, None)
            bot.answer_callback_query(update.callback_query.id, text="عمل شما Undo شد",
                                      show_alert=True)
    elif update.callback_query.data == "dislike":
        button_list = [
            InlineKeyboardButton("👎🏻   " + 'کمکی نکرد', callback_data="dislike"),
            InlineKeyboardButton("👍🏻   " + 'کمک کرد', callback_data="like"),
            InlineKeyboardButton("⛔️   " + 'ریپورت', callback_data="report"),
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
        question_id = db.find_send_answer(sender_id, update.callback_query.message.text)[1]
        db.db['answers'].delete(id=db.find_send_answer(sender_id, update.callback_query.message.text)[0])
        if db.db['answers'].find_one(questionid=question_id) is None:
            print(db.db['answers'].find_one(questionid=question_id))
            db.change_question('change_flag', question_id, False)
            bot.answer_callback_query(update.callback_query.id, text='جواب دیگری برای نمایس نیست..',
                                      show_alert=True)
        else:
            result = db.db['answers'].find_one(questionid=question_id, flagsend=False)
            bot.send_message(chat_id=db.question_by_id(question_id), text=result['atext'], reply_markup=reply_markup)
            db.change_answers('flag_send', db.find_answer_id(question_id, result['atext']), None)

    elif update.callback_query.data == "report":
        if db.report('get', update.callback_query.from_user.id, update.callback_query.message.message_id) is None:
            db.change('report', sender_id, None)
            db.report('add', update.callback_query.from_user.id, update.callback_query.message.message_id)
        else:
            db.change('removereport', sender_id, None)
            db.report('remove', update.callback_query.from_user.id, None)
            bot.answer_callback_query(update.callback_query.id, text="عمل شما Undo شد",
                                      show_alert=True)
    elif update.callback_query.data == "Qreport":
        if db.q_report('get', update.callback_query.from_user.id, update.callback_query.message.message_id) is None:
            db.change('ban', db.question_by_id(sender_id), None)
            db.q_report('add', update.callback_query.from_user.id, update.callback_query.message.message_id)
        else:
            db.change('removeban', db.question_by_id(sender_id), None)
            db.q_report('remove', update.callback_query.from_user.id, None)
            bot.answer_callback_query(update.callback_query.id, text="عمل شما Undo شد",
                                      show_alert=True)
    elif update.callback_query.data == "reply":
        bot.answer_callback_query(update.callback_query.id, text="پاسخ خود را به صورت ریپلی سوال بفرستید...",
                                  show_alert=True)


# endregion


def start(bot, update):
    update.message.reply_text('متن خوش آمد گویی')
    chatid = update.message.chat_id
    if db.get_username(chatid) and db.get_status(chatid=update.message.chat_id):
        reply_keyboard = [['/ask']]
        update.message.reply_text('برای پرسیدن سوال /ask را ارسال کنید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
    else:
        reply_keyboard = [['/user']]
        update.message.reply_text('ثبت نام شما کامل نیست لطفا با دستور /user ثبت نام کنید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))


def help(bot, update):
    pass


def answer(bot, update):
    button_list = [
        InlineKeyboardButton("👎🏻   " + 'کمکی نکرد', callback_data="dislike"),
        InlineKeyboardButton("👍🏻   " + 'کمک کرد', callback_data="like"),
        InlineKeyboardButton("⛔️   " + 'ریپورت', callback_data="report"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    q_text = update.message.reply_to_message.text  # text of the question
    text = 'ID : [' + str(update.message.chat_id) + ']' + '\n\n' + update.message.text
    if db.change('getreport', update.message.chat_id, None) > 5:
        print('report', db.change('getreport', update.message.chat_id, None))
        update.message.reply_text('شما مجاز به ارسال جواب نیستید'
                                  'اگر اشتباهی ریپورد شده اید با "" ارتباط برقرار کنید ')

    elif 'ID' in q_text:
        x = q_text.index(']')
        if db.db['questions'].find_one(id=q_text[6:x])is None or \
           db.db['questions'].find_one(id=q_text[6:x])['flag_answered']:
            db.answers_add_id(update.message.chat_id, q_text[6:x], text)
        else:
            db.answers_add_id(update.message.chat_id, q_text[6:x], text)
            db.change_question('change_flag', q_text[6:x], True)
            db.change_answers('flag_send', db.find_answer_id(q_text[6:x], text), None)
            bot.send_message(chat_id=db.question_by_id(q_text[6:x]), text=text,
                             reply_markup=reply_markup)

            bot.send_message(chat_id=config.channel_id,
                             reply_to_message_id=db.question_get(db.question_by_id(q_text[6:x]))['channel_msgid'],
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
    TOKEN = config.token
    PORT = int(os.environ.get('PORT', '5000'))
    updater = Updater(TOKEN)
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
    dp.add_handler(MessageHandler(Filters.chat(int(config.channel_id)), channel_handler,
                                  channel_post_updates=True))
    dp.add_handler(CallbackQueryHandler(callback=callback))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://persianstackoverflow.herokuapp.com/" + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
