import config
import dataset

db = dataset.connect('postgresql://postgres:{}@localhost/postgres'.format(config.dbpassword))
print("database connection OK...")

# region username


def add_username(chatid, lang, flag, last_ans, like, dislike):
    table = db['info']
    table.insert(dict(chatid=chatid, lang=lang, flag=flag, lastans=last_ans, like=like,
                      dislike=dislike))
    print("username added successfully")


def get_username(chatid):
    table = db['info']
    return table.find_one(chatid=chatid)


def change(op, chatid, lan):
    table = db['info']
    if op == 'flag':
        table.update(dict(chatid=chatid, flag=True), ['chatid'])
    elif op == 'lang':
        user = table.find_one(chatid=chatid)
        table.update(dict(chatid=chatid, lang=user['lang'] + lan + ','), ['chatid'])
    elif op == 'get':
        user = table.find_one(chatid=chatid)
        return user['lang'][:len(user['lang'])-1]
    elif op == 'del':
        table.update(dict(chatid=chatid, lang=''), ['chatid'])
# endregion


def droptable():
    table = db['info']
    table.drop()
