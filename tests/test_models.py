from unittest import TestCase
from ormini.db import *
from config import configs
from ormini.models import *


class Student(Model):
    id = IntegerField(primary_key=True)
    name = CharField()
    email = CharField(max_length=100)


class DBTests(TestCase):
    @classmethod
    def setUpClass(cls):
        if not db.connector:
            init_engine(**configs['testDB'])

    def setUp(self):
        update('drop table if exists student')

    def test_create_table_sql(self):
        s = Student()
        expect = 'create table `student` (\nemail varchar(100),\nname varchar(255),\nid int NOT NULL,\n  primary key( id )\n);'
        self.assertEqual(expect, s.create_table_sql())

    def test_create_table(self):
        s = Student()
        s.create_table()
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Ma', email='2@test.org')
        insert('student', **u2)
        r = select_one('select * from student where name=?', 'Chao').id
        self.assertEqual(1, r)
        r = select_one('select * from student where name=?', 'Ma')
        self.assertEqual(u'2@test.org', r.email)
