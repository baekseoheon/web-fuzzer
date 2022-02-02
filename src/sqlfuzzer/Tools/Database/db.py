import json
from treelib import Tree, Node

tree_list = []
all_strings = []

def init_stats(filename):
    """
        json 파일에서 통계를 불러오고 사용 가능한 다음 문자 목록과 그 확률에 대한 두 번째 목록을 포함하는 사전 반환
    """ 

    with open(filename) as json_file:
        data = json.load(json_file)

    statistics = {}
    for chr, stats in data.items():
        statistics[chr] = (list(stats.keys()), list(stats.values()))

    return statistics


def new_string_tree(s, id):
    """ 
        첫 문자열을 넣을 트리 생성 후 반환
    """
    new_tree = Tree()
    new_tree.create_node(s, id)

    tree_list.append(new_tree)
    all_strings.append(s)
    return new_tree


def add_son(father_id, son_string, son_id):
    """
        father_id를 사용하여 특정 노드에 자식 노드를 추가한다.
        father_id를 포함하고 있다면 노드를 생성하고 True를 반환하고 아니면 False를 반환한다.
    """
    for tree in tree_list:
        if tree.contains(father_id):
            tree.create_node(son_string, son_id, parent=father_id)
            all_strings.append(son_string)
            return True

    return False


def is_created(s):
    """
        반복되는 문자열이 없는지 확인
    """
    return s in all_strings


def get_value(id):
    """
        ID를 가져와 트리에 저장된 데이터 반환 
        ID가 없으면 False 반환
    """
    for tree in tree_list:
        if tree.contains(id):
            return tree[id].tag

    return "False"

if __name__ == '__main__':
    print(init_stats("odds.json"))
