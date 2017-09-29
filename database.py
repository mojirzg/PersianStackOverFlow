import config
import dataset
import psycopg2

db = dataset.connect('postgresql://postgres:{}@localhost/postgres'.format(config.dbpassword))
print("database connection OK...")
conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password=config.dbpassword)
cursor = conn.cursor()
# region username


def add_username(chatid, lang, flag, last_ans, like, dislike):
    table = db['info']
    table.insert(dict(chatid=chatid, lang=lang, flag=flag, lastans=last_ans, like=like,
                      dislike=dislike))
    print("username added successfully")


def get_username(chatid):
    table = db['info']
    return table.find_one(chatid=chatid)


def change(op, chatid, arg):
    table = db['info']
    if op == 'flag':
        table.update(dict(chatid=chatid, flag=True), ['chatid'])
    elif op == 'lang':
        user = table.find_one(chatid=chatid)
        table.update(dict(chatid=chatid, lang=user['lang'] + arg + ','), ['chatid'])
    elif op == 'get':
        user = table.find_one(chatid=chatid)
        return user['lang'][:len(user['lang'])-1]
    elif op == 'del':
        table.update(dict(chatid=chatid, lang=''), ['chatid'])
    elif op == 'time':
        table.update(dict(chatid=chatid, lastans=arg), ['chatid'])
    elif op == 'gettime':  # returns the last send question time
        result = table.find_one(chatid=chatid)
        return result['lastans']


# endregion


def who_to_ask(lan):
    table = db['info']
    result = table.find(flag=True)
    user = []
    for row in result:
        if lan in row['lang'][:len(row['lang']) - 1]:
            user.append(row['chatid'])
    return user


# region Questions

def question_add_id(chatid):
    table = db['questions']
    table.insert(dict(chatid=chatid, lan='', subject='', qtext='', photo='', ans1='', ans2='',
                      ans3='', asked=''))


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


def get(chatid):
    table = db['questions']
    result = table.find_one(chatid=chatid)
    return result
# endregion


def droptable():
    table = db['info']
    table.drop()

def droptable2():
    table = db['info']
    table.drop()


