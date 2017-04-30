import json
from ormini.db import insert


def load_data(model, file_path):
    with open(file_path) as data_file:
        data = json.load(data_file)
    for d in data:
        insert(model, **d)
