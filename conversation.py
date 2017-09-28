from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import database as db


# region first


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

    db.add_username(update.message.chat_id, '', True, 0, 0, 0, )
    return lan


def flag_no(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'C#']]
    update.message.reply_text("سوال دیگران برای شما ارسال نمیشود ",
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("لطفا موارد مورد نظر خود را انتخاب کنید ",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))
    db.add_username(update.message.chat_id, '', False, 0, 0, 0, )
    return lan


def lan(bot, update):
    reply_keyboard = [['Python', 'Photoshop', 'C#'], ['/Done', '/Cancel']]
    if update.message.text in db.change('get', update.message.chat_id, None):
        bot.send_message(chat_id=update.message.chat_id, text="قبلا انتخاب شده")
        update.message.reply_text("اگر انتخاب شما تمام شده /done را ارسال کنید",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True, resize_keyboard=True))
        return lan
    else:
        db.change('lang', update.message.chat_id, lan=update.message.text)
        print(db.get_username(update.message.chat_id))
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
    reply_keyboard = [['Python', 'Photoshop', 'C#'], ['/Done', '/Cancel']]
    db.change('del', update.message.chat_id, None)
    update.message.reply_text('موارد قبلی پاک شد لطفا دوباره انتخاب کنید',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True, resize_keyboard=True))

    return lan


def check(bot, update):
    if update.message.text == 'بله':
        update.message.reply_text('اطلاعات شما ثبت شد میتوانید سوال خود را بپرسید', reply_markup=ReplyKeyboardRemove())
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

            lan: [RegexHandler('^(Python|Photoshop|C#)$', lan),
                  CommandHandler('Done', lan_done),
                  CommandHandler('Cancel', lan_cancel)],

            lan_done: [RegexHandler('^(خیر)$', lan_cancel),
                       RegexHandler('^(بله)$', check)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
# endregion

