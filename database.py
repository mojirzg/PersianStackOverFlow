import config
import dataset
import psycopg2

# region Connection
db = dataset.connect('postgresql://{}:{}@{}/{}'.format(config.dbusername,
                                                       config.dbpassword,
                                                       config.host,
                                                       config.database))
print("database connection OK...")


# endregion

# region username


def add_username(chatid, flag, last_ans):
    table = db['info']
    table.insert(dict(chatid=chatid, lang='', flag=flag, lastans=last_ans, like=0,
                      report=0, ban=0, status=False))
    print("username added successfully")


def get_username(chatid):
    table = db['info']
    return table.find_one(chatid=chatid)


def change(op, chatid, arg):
    table = db['info']
    if op == 'flag':
        table.update(dict(chatid=chatid, flag=arg), ['chatid'])
    elif op == 'lang':
        user = table.find_one(chatid=chatid)
        table.update(dict(chatid=chatid, lang=user['lang'] + arg + ','), ['chatid'])
    elif op == 'get':
        user = table.find_one(chatid=chatid)
        return user['lang'][:len(user['lang']) - 1]
    elif op == 'del':
        table.update(dict(chatid=chatid, lang=''), ['chatid'])
    elif op == 'time':
        table.update(dict(chatid=chatid, lastans=arg), ['chatid'])
    elif op == 'gettime':  # returns the last send question time
        result = table.find_one(chatid=chatid)
        return result['lastans']
    elif op == 'addlike':
        result = table.find_one(chatid=chatid)
        like = int(result['like']) + 1
        table.update(dict(chatid=chatid, like=like), ['chatid'])
    elif op == 'removelike':
        result = table.find_one(chatid=chatid)
        like = int(result['like']) - 1
        table.update(dict(chatid=chatid, like=like), ['chatid'])
        return like
    elif op == 'report':
        result = table.find_one(chatid=chatid)
        report = int(result['report']) + 1
        table.update(dict(chatid=chatid, report=report), ['chatid'])
        return report
    elif op == 'removereport':
        result = table.find_one(chatid=chatid)
        report = int(result['report']) - 1
        table.update(dict(chatid=chatid, report=report), ['chatid'])
        return report
    elif op == 'getreport':
        result = table.find_one(chatid=chatid)
        return result['report']
    elif op == 'ban':
        result = table.find_one(chatid=chatid)
        ban = int(result['ban']) + 1
        table.update(dict(chatid=chatid, ban=ban), ['chatid'])
        return ban
    elif op == 'getban':
        result = table.find_one(chatid=chatid)
        ban = (result['ban'])
        return ban
    elif op == 'removeban':
        result = table.find_one(chatid=chatid)
        ban = int(result['ban']) - 1
        table.update(dict(chatid=chatid, ban=ban), ['chatid'])
        return ban


def get_status(chatid):
    table = db['info']
    result = table.find_one(chatid=chatid)
    return result


# endregion

# region Questions


def question_add_id(chatid):
    table = db['questions']
    table.insert(dict(chatid=chatid, lan='', subject='', qtext='', photo='', flag_answered=False,
                      asked='', channel_msgid=''))


def change_question(op, chatid, arg):
    table = db['questions']
    if op == 'subject':
        table.update(dict(chatid=chatid, subject=arg), ['chatid'])
    elif op == 'asked':
        table.update(dict(chatid=chatid, asked=arg), ['chatid'])
    elif op == 'text':
        table.update(dict(chatid=chatid, qtext=arg), ['chatid'])
    elif op == 'lan':
        table.update(dict(chatid=chatid, lan=arg), ['chatid'])
    elif op == 'msgid':
        table.update(dict(id=chatid, channel_msgid=arg), ['id'])
    elif op == 'change_flag':
        table.update(dict(id=chatid, flag_answered=arg), ['id'])


def question_get(chatid):
    table = db['questions']
    result = table.find_one(chatid=chatid)
    return result


def q_id(chatid):
    table = db['questions']
    result = table.find(chatid=chatid)
    temp = []
    for row in result:
        temp.append(row['id'])
    return max(temp)


def question_by_id(sender_id):  # to Find the chat id of the one who asked the question
    table = db['questions']
    result = table.find_one(id=sender_id)
    return result['chatid']


def who_to_ask(lan):
    table = db['info']
    result = table.find(flag=True)
    user = []
    for row in result:
        if lan in row['lang'][:len(row['lang']) - 1]:
            user.append(row['chatid'])
    return user


# endregion

# region Answers
def answers_add_id(chatid, questionid, atext):
    table = db['answers']
    table.insert(dict(chatid=chatid, questionid=questionid, atext=atext, flagsend=False))


def answers_get(questionid):
    table = db['answers']
    result = table.find_one(questionid=questionid)
    return result


def find_answer_id(questionid, text):
    table = db['answers']
    result = table.find_one(questionid=questionid, atext=text)
    return result['id']


def change_answers(op, answer_id, arg):
    table = db['answers']
    if op == 'flag_send':
        table.update(dict(id=answer_id, flagsend=True), ['id'])


def find_send_answer(sender_id, text):
    table = db['answers']
    result = table.find_one(chatid=sender_id, atext=text, flagsend=True)
    return result['id'], result['questionid']

# endregion

# region callback
def likes(op, chatid, msgid):
    table = db['likes']
    if op == 'add':
        table.insert(dict(chatid=chatid, msgid=msgid))
    elif op == 'get':
        result = table.find_one(msgid=msgid, chatid=chatid)
        print('3', result)
        return result
    elif op == 'remove':
        table.delete(chatid=chatid)


def q_report(op, chatid, msgid):
    table = db['qreport']
    if op == 'add':
        table.insert(dict(chatid=chatid, msgid=msgid))
    elif op == 'get':
        result = table.find_one(msgid=msgid, chatid=chatid)
        print(result)
        return result
    elif op == 'remove':
        table.delete(chatid=chatid)


def report(op, chatid, msgid):
    table = db['report']
    if op == 'add':
        table.insert(dict(chatid=chatid, msgid=msgid))
    elif op == 'get':
        result = table.find_one(msgid=msgid, chatid=chatid)
        print(result)
        return result
    elif op == 'remove':
        table.delete(chatid=chatid)


# endregion


def drop_table():
    table = db['']
    table.drop()
