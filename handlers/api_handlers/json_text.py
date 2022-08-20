import re
import json

def json_mod(text, file_name):
    data = json.loads(text)
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    with open(file_name, 'r', encoding='utf-8') as file:
        mod_text = json.load(file)

    return mod_text