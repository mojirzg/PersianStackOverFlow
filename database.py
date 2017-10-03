import config
import dataset
import psycopg2

# region Connection
db = dataset.connect('postgresql://postgres:{}@localhost/postgres'.format(config.dbpassword))
print("database connection OK...")


# endregion

# region Databasae Info

def database_info():
    r = '\033[91m'
    b = '\033[94m'
    d = '\033[00m'
    #db['info'].drop()
    print(r, 'tables:', db.tables)
    print(b, 'info:', db['info'].columns)
    print(b, 'questions:', db['questions'].columns , d)

# endregion

# region username


def add_username(chatid, flag, last_ans):
    table = db['info']
    table.insert(dict(chatid=chatid, lang='', flag=flag, lastans=last_ans, like=0,
                      report=0, ban=0 , status=0))
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
        print(result['like'])
    elif op == 'report':
        result = table.find_one(chatid=chatid)
        report = int(result['report']) + 1
        table.update(dict(chatid=chatid, report=report), ['chatid'])
        return report


# endregion

# region Questions


def question_add_id(chatid):
    table = db['questions']
    table.insert(dict(chatid=chatid, lan='', subject='', qtext='', photo='', ans1='', ans2='',
                      ans3='', asked='', channel_msgid=''))


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
        table.update(dict(chatid=chatid, channel_msgid=arg), ['chatid'])


def get(chatid):
    table = db['questions']
    result = table.find_one(chatid=chatid)
    return result


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

def likes(op, chatid, msgid):
    table = db['likes']
    table.insert(dict(chatid=chatid, msgid=msgid))


def droptable():
    table = db['']
    table.drop()
