import numpy as np
import uuid
import logging

from Tools.Database import db

sql_logger = logging.getLogger("SQL_Generator")

MAX_RECURSION = 5
MAX_REPS = 10
opening_chars = ["\'", "\"", ")", "1"]
comment_chars = ["#", "--", "'vRxe'='vRxe"]
string_trees = []


stats = None


def init_stats(filename):
    #sql_generator 모듈의 통계를 초기화합니다.
    global stats

    stats = db.init_stats(filename)

def is_duplicated(s):
    # 인자끝에 3개 이상의 동일한 문자가 있는지 확인하여 True 또는 False를 반환시킨다.
    if len(s) < 2:
        return False
    return s[-1] == s[-2]

def create_string(call_time=0):
    # 문자열을 만들고 ID와 그 문자열을 반환시킨다.
    id = uuid.uuid4()
    s = np.random.choice(opening_chars)
    # 자동화
    current_char = s
    while current_char in opening_chars:
        rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])
        if rand_s not in opening_chars:
            if db.is_created(s) and call_time < MAX_RECURSION: # Avoid duplicates
                sql_logger.debug(" String already exist. Recursion Num: {}".format(call_time+1))
                return create_string(call_time+1)
            string_trees.append(db.new_string_tree(s, id))
            new_id = uuid.uuid4()
            s += " " + rand_s
            db.add_son(id, s, new_id)
            return new_id, s
        if not is_duplicated(s):
            s += rand_s

def upgrade(id, call_time=0):
    #String에 새로운 주석을 추가 시킨다.
    #String의 특정한 id를 가져와서 String과  더불어 새로운 id를 반환시킨다. String이 주석으로 끝날 경우 그대로 String을 반환시킨다.
    new_id = uuid.uuid4()
    s = db.get_value(id)
    current_char = s.split()[-1]
    if current_char in comment_chars:
        return id, s

    rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])
    # 완성된 문자열은 걸러낸다.
    count = 0
    while rand_s in comment_chars:
        count += 1
        if count > MAX_REPS:
            s += " " + rand_s
            if db.is_created(s) and call_time < MAX_RECURSION: # Avoid duplicates
                sql_logger.debug(" String already exist. Recursion Num: {}".format(call_time+1))
                return upgrade(id, call_time+1)
            db.add_son(id, s, new_id)
            return new_id, s
        rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])

    s += " " + rand_s
    if db.is_created(s) and call_time < MAX_RECURSION: # Avoid duplicates
        sql_logger.debug(" String already exist. Recursion Num: {}".format(call_time+1))
        return upgrade(id, call_time+1)

    db.add_son(id, s, new_id)
    return new_id, s

def finishing_touches(id):
    #String의 ID를 얻고 문자열에 주석을 추가합니다.
    #이 함수는 새 문자열과 새 ID를 반환합니다.
    #주석을 추가할 수 없는 경우 함수는 명령을 추가하고 반환합니다.
    new_id = uuid.uuid4()
    s = db.get_value(id)
    current_char = s.split()[-1]
    if current_char in comment_chars:
        return id, s

    rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])

    count = 0
    while rand_s not in comment_chars:
        count += 1
        if count > MAX_REPS:
            s += " " + rand_s
            db.add_son(id, s, new_id)
            return new_id, s
        rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])

    s += " " + rand_s
    db.add_son(id, s, new_id)
    return new_id, s

if __name__ == '__main__':
    print(stats)