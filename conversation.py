from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import ConversationHandler
import database as db

langs = []


def start(bot, update):
    reply_keyboard = [['خیر', 'بله']]

    update.message.reply_text(
        "آیا مایل به پاسخ دادن سوال دیگران هستید؟",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return flag_yes


def flag_yes(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'C#']]
    update.message.reply_text("سوال دیگران برای شما ارسال میشود ",
                              reply_markup=ReplyKeyboardRemove())

    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))

    global flag
    flag = True
    return lan


def flag_no(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'C#']]
    update.message.reply_text("سوال دیگران برای شما ارسال نمیشود ",
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    global flag
    flag = False
    return lan


def lan(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'C#'], ['/Done', '/Cancel']]
    if update.message.text in langs:
        bot.send_message(chat_id=update.message.chat_id, text="قبلا انتخاب شده",
                         show_alert=True)
        update.message.reply_text("اگر انتخاب شما تمام شده /done را ارسال کنید",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True, resize_keyboard=True))
        return lan
    else:
        langs.append(update.message.text)
        update.message.reply_text("اگر انتخاب شما تمام شده /done را ارسال کنید",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True, resize_keyboard=True))


def lan_done(bot, update):
    reply_keyboard = [['خیر', 'بله']]
    update.message.reply_text("موارد انتخابی شما:\n" + str(langs),
                              replay_markup=ReplyKeyboardRemove())
    update.message.reply_text("آیا درست است؟",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    return lan_done


def lan_cancel(bot, update):
    langs.clear()
    update.message.reply_text('موارد قبلی پاک شد لطفا دوباره انتخاب کنید')
    return lan


def check(bot, update):
    if update.message.text == 'بله':
        update.message.reply_text('اطلاعات شما ثبت شد میتوانید سوال خود را بپرسید', reply_markup=ReplyKeyboardRemove())
        user = db.UserName(update.message.chat_id, str(langs), flag, 0, 0, 0)
        db.UserName.add_username(user)
        return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    print("User %s canceled the conversation." % user.first_name)
    return ConversationHandler.END
