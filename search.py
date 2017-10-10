import database as db
import re


def search(question):
    table = db.db['questions']
    question = question  # question text from answers
    dic = {}
    words = re.findall(r'\w+', question)
    q_id = []
    for column in table:
        counter = 0
        for word in words:
            if word in column['qtext']:
                counter += 1
        dic[counter] = column['qtext']

    try:
        matched_key = tuple(dic.keys())
        mk_sorted = sorted(matched_key, reverse=True)
        if mk_sorted[0] and mk_sorted[0] > 1:
            print(dic[mk_sorted[0]])
            result = table.find_one(qtext=dic[mk_sorted[0]])
            print('search 24', dic[mk_sorted[0]])
            q_id.append(result['id'])
        else:
            return None  # if not found
        if mk_sorted[1] and mk_sorted[1] > 1:
            print(dic[mk_sorted[1]])
            result = table.find_one(qtext=dic[mk_sorted[1]])
            q_id.append(result['id'])
        if mk_sorted[2] and mk_sorted[2] > 1:
            print(dic[mk_sorted[2]])
            result = table.find_one(qtext=dic[mk_sorted[2]])
            q_id.append(result['id'])
            print(q_id)
            return q_id

    except Exception as e:
        print(e)

