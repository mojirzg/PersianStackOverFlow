import database as db
import re


def search(question, question_id):
    table = db.db['questions']
    question = question  # question text
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
        match = 1
        if mk_sorted[0] and mk_sorted[0] > match:
            for item in mk_sorted:
                if item and item > match:
                    result = table.find_one(qtext=dic[item])
                    if result['id'] != question_id:
                        q_id.append(result['id'])
            return q_id
        else:
            return None

    except Exception as e:
        print(e)

