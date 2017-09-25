import config
import dataset

db = dataset.connect('postgresql://postgres:{}6654@localhost/postgres'.format(config.dbpassword))
print("database connection OK...")


class UserName:
    def __init__(self, chatid, lang, flag, last_ans, like, dislike):
        self.chatid = chatid
        self.lang = lang
        self.flag = flag
        self.last_ans = last_ans
        self.like = like
        self.dislike = dislike

    def add_username(self):
        print(self.chatid, self.lang, self.flag, self.last_ans, self.like, self.dislike)
        table = db['info']
        table.insert(dict(chatid=self.chatid, lang=self.lang, lastans=self.last_ans, like=self.like,
                          dislike=self.dislike))
        print("username added successfully")

    def get_username(chatid):
        table = db['info']
        return table.find_one(chatid=chatid)

    def get_user_info(self):
        print(self.chatid, self.flag, self.lang, self.last_ans, self.like, self.dislike)


def droptable():
    table = db['info']
    table.drop()
