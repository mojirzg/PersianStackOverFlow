import database as db
from fuzzywuzzy import fuzz


def search(question, question_id):
    table = db.db['questions']
    question = question  # question text
    q_id = []
    for column in table:
        if fuzz.token_sort_ratio(column['qtext'], question) > 70:
            if column['id'] != question_id and column['flag_answered']:
                q_id.append(column['id'])
    print(q_id)
    if q_id:
        return q_id
