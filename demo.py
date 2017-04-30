from ormini.models import *
from ormini.fields import *
from ormini.db import *
from ormini.load import load_data
from config import configs


class Sailor(Model):
    sid = IntegerField(primary_key=True, db_index=True)
    sname = CharField(max_length=20, not_null=True)
    rating = IntegerField()
    age = FloatField()


class Reserve(Model):
    bid = IntegerField(primary_key=True, db_index=True)
    sid = ForeignKeyField(Sailor, related_field='sid', on_delete='cascade')
    day = CharField(max_length=20)

init_engine(**configs['testDB'])


def clear():
    update('drop table if exists reserve')
    update('drop table if exists sailor')

