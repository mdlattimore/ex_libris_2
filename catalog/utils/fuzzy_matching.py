# utils/fuzzy_matching.py

from rapidfuzz import fuzz, utils
from simple_name_parser import NameParser
from unidecode import unidecode
import re

def normalize_name(name):
    name_parser = NameParser()
    #strip accents/diacriticals
    name = unidecode(name)
    name_list = name.split()
    if name_list[0].endswith(','):
        if len(name_list) > 1:
            part1 = " ".join(name_list[1:])
            part2 = name_list[0].rstrip(',')
            name = f'{part1} {part2}'.strip()
        else:
            name = name_list[0].rstrip(',')
    parsed_name = name_parser.parse_name(name)
    suffix = parsed_name.suffix
    surname = parsed_name.surname
    rest_name = parsed_name.given_name + ' ' + parsed_name.middle_name
    rest_name1 = rest_name.replace(".", " ")
    initials = "".join([i[0] for i in rest_name1.split()])
    return f"{initials.lower()} {surname.lower()} {suffix.lower()}".strip()


def name_match(source, target):
    source = normalize_name(source)
    target = normalize_name(target)
    return fuzz.token_sort_ratio(source, target)


def normalize_title(title):
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title).strip()
    return title

def title_match(source, target):
    source = normalize_title(source)
    target = normalize_title(target)
    return fuzz.token_set_ratio(source, target)


if __name__ == '__main__':
    import json
    with open('../names.json', 'r') as f:
        names = json.load(f)
    results = []
    for name, value in names.items():

        for n in value:
            results.append((n, name, name_match(n, name)))
        results.sort(key=lambda x: x[2], reverse=True)
    for r in results:
        print(f"{r[0]}: {r[1]} -- >{r[2]}")
