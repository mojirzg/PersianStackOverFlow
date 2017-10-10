from telegram import *
from telegram.ext import *
from search import search
import database as db
import datetime
import config
from main import build_menu

# region First time


def start(bot, update):
    if db.get_username(update.message.chat_id) and db.get_status(update.message.chat_id):
        reply_keyboard = [['/ask']]
        update.message.reply_text('شما این مراحل را طی کرده اید')  # todo edit information
        update.message.reply_text('ّبرای پرسیدن سوال /ask را ارسال کنید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return ConversationHandler.END
    elif db.get_username(update.message.chat_id) and not db.get_status(update.message.chat_id):
        db.db['info'].delete(chatid=update.message.chat_id)
        reply_keyboard = [['خیر', 'بله']]
        update.message.reply_text(
            "آیا مایل به پاسخ دادن سوال دیگران هستید؟",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return flag_yes
    else:
        reply_keyboard = [['خیر', 'بله']]
        update.message.reply_text(
            "آیا مایل به پاسخ دادن سوال دیگران هستید؟",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return flag_yes


def flag_yes(bot, update):
    db.add_username(update.message.chat_id, True, datetime.datetime.now())
    reply_keyboard = [['Python', 'Photoshop', 'SQL']]
    update.message.reply_text("سوال دیگران برای شما ارسال میشود ",
                              reply_markup=ReplyKeyboardRemove())

    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))

    return lan


def flag_no(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'SQL']]
    update.message.reply_text("سوال دیگران برای شما ارسال نمیشود ",
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    db.add_username(update.message.chat_id, False, '')
    return lan


def lan(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'SQL'], ['/Cancel', '/Reset', '/Done']]
    if update.message.text in db.change('get', update.message.chat_id, update.message.text):
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
    reply_keyboard = [['Python', 'Photoshop', 'SQL'], ['/Cancel', '/Reset', '/Done']]
    db.change('del', update.message.chat_id, None)
    update.message.reply_text("لطفا دوباره انتخاب کنید",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))

    return lan


def check(bot, update):
    reply_keyboard = [['/ask']]
    if update.message.text == 'بله':
        table = db.db['info']
        chatid = update.message.chat_id
        table.update(dict(chatid=chatid, status=True), ['chatid'])
        update.message.reply_text('اطلاعات شما ثبت شد میتوانید سوال خود را بپرسید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   resize_keyboard=True))
        db.get_username(update.message.chat_id)
        return ConversationHandler.END


def cancel(bot, update):
    reply_keyboard = [['/user']]
    user = update.message.from_user
    db.db['info'].delete(chatid=update.message.chat_id)
    update.message.reply_text('عملیات ثبت نام متوقف شد برای استفاده از بات لطفا با راسال /user ثبت نام کنید',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
    print("User %s canceled the conversation." % user.first_name)
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('user', start)],

    states={
        flag_yes: [RegexHandler('^(بله)$', flag_yes),
                   RegexHandler('^(خیر)$', flag_no)],

        lan: [RegexHandler('^(Python|Photoshop|SQL)$', lan),
              CommandHandler('Done', lan_done),
              CommandHandler('Reset', lan_cancel)],

        lan_done: [RegexHandler('^(خیر)$', lan_cancel),
                   RegexHandler('^(بله)$', check)],

    },

    fallbacks=[CommandHandler('Cancel', cancel)]
)


# endregion

# region Question


def start_question(bot, update):
    if db.get_status(update.message.chat_id):
        result = db.change('get', update.message.chat_id, None).split(',')
        reply_keyboard = [result]
        db.question_add_id(update.message.chat_id)
        update.message.reply_text(
            "سوال در مور چه مبحثی است",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

        return language
    else:
        reply_keyboard = [['/user']]
        update.message.reply_text('شما ثبت نام نکرده اید لطفا با استفاده از دستور /user ثبت نام کنید',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))


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
    result = db.question_get(update.message.chat_id)
    reply_keyboard = [['cancel', 'ok']]
    update.message.reply_text('مبحث : ' + result['lan'] +
                              '\nموضوع : ' + result['subject'] +
                              '\nمتن : ' + result['qtext'] +
                              '\nبرای ارسال ok و برای ویرایش cancel را ارسال کنید',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))
    return history


def history(bot, update):
    reply_keyboard = [['cancel'], ['سوال مورد نظرم یافت نشد']]
    q_id = db.q_id(update.message.chat_id)
    chat_id = update.message.chat_id
    history_question_id = search(db.db['questions'].find_one(id=q_id)['qtext'])
    update.message.reply_text('سوال های مشابه یافت شده'
                              'برای دیدن پاسخ مورد نظر ans را بر روی خود سوال ریپلی کنید'
                              , reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                 resize_keyboard=True))
    for item in history_question_id:
        result = db.db['questions'].find_one(id=item)
        bot.send_message(chat_id=chat_id, text=result['qtext'])

    return send


def send(bot, update):
    result = db.question_get(update.message.chat_id)
    send_message = result['asked'][1:len(result['asked']) - 1].split(',')
    button_list = [
        InlineKeyboardButton("⛔️   " + 'ریپورت', callback_data="Qreport"),
        InlineKeyboardButton("↪️   " + 'پاسخ دادن', callback_data="reply"),
    ]  # todo only send for top likes
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    for ID in send_message:
        if datetime.datetime.now() - db.change('gettime', ID, None) > datetime.timedelta(minutes=2) and \
                                    str(update.message.chat_id) != ID:
            # don't send if last send was before 2 minutes
            bot.send_message(chat_id=ID, text='ID : [' + str(db.q_id(update.message.chat_id)) + ']'
                                              '\nمبحث : ' + result['lan'] +
                                              '\nموضوع : ' + result['subject'] +
                                              '\nمتن : ' + result['qtext'],
                             reply_markup=reply_markup)

            db.change('time', ID, datetime.datetime.now())
        elif datetime.datetime.now() - db.change('gettime', ID, None) < datetime.timedelta(minutes=2):
            print(ID, "2min not passed")
    update.message.reply_text('ارسال شد', reply_markup=ReplyKeyboardRemove())
    s = bot.send_message(chat_id=config.channel_id, text='ID : [' + str(db.q_id(update.message.chat_id)) + ']' +
                                                         '\nمبحث : ' + result['lan'] +
                                                         '\nموضوع : ' + result['subject'] +
                                                         '\nمتن : ' + result['qtext'])
    db.change_question('msgid', db.q_id(update.message.chat_id), s.message_id)
    return ConversationHandler.END


def cancel2(bot, update):
    user = update.message.from_user
    reply_keyboard = [['/ask']]
    update.message.reply_text('ارسال سوال لغو شد')
    update.message.reply_text('با استفاده از دستور /ask سوال خود را بپرسید',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True))
    print("User %s canceled the conversation." % user.first_name)
    return ConversationHandler.END


conv_handler_question = ConversationHandler(
    entry_points=[CommandHandler('ask', start_question)],

    states={
        language: [RegexHandler('^(Python|Photoshop|SQL)$', language)],

        subject: [MessageHandler(Filters.text, subject)],

        text: [MessageHandler(Filters.text, text)],

        history: [RegexHandler('^(ok)$', history),
                  RegexHandler('^(cancel)$', cancel2)],

        send: [RegexHandler('^(سوال مورد نظرم یافت نشد)$', send),
               RegexHandler('^(cancel)$', cancel2)]

    },

    fallbacks=[CommandHandler('cancel', cancel2)])
# endregion
