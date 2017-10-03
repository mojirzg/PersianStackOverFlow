from telegram import *
from telegram.ext import *
import database as db
import datetime
import config
from main import build_menu

# region First time


def start(bot, update):
    reply_keyboard = [['خیر', 'بله']]
    update.message.reply_text(
        "آیا مایل به پاسخ دادن سوال دیگران هستید؟",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return flag_yes


def flag_yes(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'SQL']]
    update.message.reply_text("سوال دیگران برای شما ارسال میشود ",
                              reply_markup=ReplyKeyboardRemove())

    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))

    db.add_username(update.message.chat_id, '', True, datetime.datetime.now(), 0, 0, )
    return lan


def flag_no(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'SQL']]
    update.message.reply_text("سوال دیگران برای شما ارسال نمیشود ",
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    db.add_username(update.message.chat_id, '', False, 0, 0, 0, )
    return lan


def lan(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'SQL'], ['/Done', '/Cancel']]
    if update.message.text in db.change('get', update.message.chat_id, None):
        bot.send_message(chat_id=update.message.chat_id, text="قبلا انتخاب شده")
        update.message.reply_text("اگر انتخاب شما تمام شده /done را ارسال کنید",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True, resize_keyboard=True))
        return lan
    else:
        db.change('lang', update.message.chat_id, update.message.text)
        update.message.reply_text("اگر انتخاب شما تمام شده /done را ارسال کنید",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True, resize_keyboard=True))


def lan_done(bot, update):
    reply_keyboard = [['خیر', 'بله']]
    update.message.reply_text("موارد انتخابی شما:\n" + str(db.change('get', update.message.chat_id, None)),
                              replay_markup=ReplyKeyboardRemove())
    update.message.reply_text("آیا درست است؟",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    return lan_done


def lan_cancel(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'SQL'], ['/Done', '/Cancel']]
    db.change('del', update.message.chat_id, None)
    update.message.reply_text("آیا درست است؟",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))

    return lan


def check(bot, update):
    reply_keyboard = [['/ask']]
    if update.message.text == 'بله':
        update.message.reply_text('اطلاعات شما ثبت شد میتوانید سوال خود را بپرسید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   resize_keyboard=True))
        db.get_username(update.message.chat_id)
        return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    print("User %s canceled the conversation." % user.first_name)
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('user', start)],

    states={
        flag_yes: [RegexHandler('^(بله)$', flag_yes),
                   RegexHandler('^(خیر)$', flag_no)],

        lan: [RegexHandler('^(Python|Photoshop|SQL)$', lan),
              CommandHandler('Done', lan_done),
              CommandHandler('Cancel', lan_cancel)],

        lan_done: [RegexHandler('^(خیر)$', lan_cancel),
                   RegexHandler('^(بله)$', check)],

    },

    fallbacks=[CommandHandler('cancel', cancel)]
)


# endregion

# region Question


def start_question(bot, update):
    result = db.change('get', update.message.chat_id, None).split(',')
    reply_keyboard = [result]
    db.question_add_id(update.message.chat_id)
    update.message.reply_text(
        "سوال در مور چه مبحثی است",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return language


def language(bot, update):
    db.change_question('lan', update.message.chat_id, update.message.text)
    db.change_question('asked', update.message.chat_id, db.who_to_ask(update.message.text))
    update.message.reply_text("موضوع سوال شما چیست؟ ",
                              reply_markup=ReplyKeyboardRemove())

    return subject


def subject(bot, update):
    db.change_question('subject', update.message.chat_id, update.message.text)
    update.message.reply_text("متن سوال را بفرستید")
    return text


def text(bot, update):
    db.change_question('text', update.message.chat_id, update.message.text)
    result = db.get(update.message.chat_id)
    reply_keyboard = [['cancel', 'ok']]
    update.message.reply_text('مبحث : ' + result['lan'] +
                              '\nموضوع : ' + result['subject'] +
                              '\nمتن : ' + result['qtext'] +
                              '\nبرای ارسال ok و برای ویرایش cancel را ارسال کنید',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    return send


def send(bot, update):
    result = db.get(update.message.chat_id)
    send_message = result['asked'][1:len(result['asked']) - 1].split(',')
    button_list = [
        InlineKeyboardButton("⛔️   " + 'ریپورت', callback_data="Qreport"),
        InlineKeyboardButton("↪️   " + 'پاسخ دادن', callback_data="reply"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    for ID in send_message:
        if datetime.datetime.now() - db.change('gettime', ID, None) > datetime.timedelta(seconds=2):
                # and \
                #        str(update.message.chat_id) != ID:
            # don't send if last send was before 2 minutes
            bot.send_message(chat_id=ID, text='ID : [' + str(result['id']) + ']'
                                              '\nمبحث : ' + result['lan'] +
                                              '\nموضوع : ' + result['subject'] +
                                              '\nمتن : ' + result['qtext'],
                             reply_markup=reply_markup)

            db.change('time', ID, datetime.datetime.now())
        elif datetime.datetime.now() - db.change('gettime', ID, None) < datetime.timedelta(minutes=2):
            print(ID, "2min not passed")
    update.message.reply_text('ارسال شد', reply_markup=ReplyKeyboardRemove())
    s = bot.send_message(chat_id=config.channel_id, text='ID : [' + str(result['id']) + ']'
                                                         '\nمبحث : ' + result['lan'] +
                                                         '\nموضوع : ' + result['subject'] +
                                                         '\nمتن : ' + result['qtext'])
    db.change_question('msgid', update.message.chat_id, s.message_id)
    return ConversationHandler.END


def cancel2(bot, update):
    user = update.message.from_user
    print("User %s canceled the conversation." % user.first_name)
    return ConversationHandler.END


conv_handler_question = ConversationHandler(
    entry_points=[CommandHandler('ask', start_question)],

    states={
        language: [RegexHandler('^(Python|Photoshop|SQL)$', language)],

        subject: [MessageHandler(Filters.text, subject)],

        text: [MessageHandler(Filters.text, text)],

        send: [RegexHandler('^(ok)$', send),
               RegexHandler('^(cancel)$', cancel2)]

    },

    fallbacks=[CommandHandler('cancel', cancel2)])
# endregion

# todo if user conv is not finished delete the row
# todo reply button for like dislike and report
# todo add like and dislike for each answer
# todo bug one can add username twice

