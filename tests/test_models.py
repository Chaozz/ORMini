from unittest import TestCase
from ormini.db import *
from config import configs
from ormini.models import *
from ormini.fields import IntegerField


class Student(Model):
    id = IntegerField(primary_key=True, db_index=True)
    name = CharField(db_index=True)
    email = CharField(max_length=100)


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        if not db.connector:
            init_engine(**configs['testDB'])

    def setUp(self):
        update('drop table if exists student')
        Student.create_table()

    def test_create_table_sql(self):
        s = Student()
        expect = 'create table `student` (\nemail varchar(100),\nname varchar(255),\nid int NOT NULL,\n  primary key( id )\n);'
        self.assertEqual(expect, s.create_table_sql())

    def test_create_table(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Ma', email='2@test.org')
        insert('student', **u2)
        r = select_one('select * from student where name=?', 'Chao').id
        self.assertEqual(1, r)
        r = select_one('select * from student where name=?', 'Ma')
        self.assertEqual(u'2@test.org', r.email)

    def test_get_by_id(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Ma', email='2@test.org')
        insert('student', **u2)
        r=Student.get_by_pk(1)
        self.assertEqual('Chao', r.name)
        r = Student.get_by_pk(2)
        self.assertEqual('Ma', r.name)

    def test_get(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Ma', email='2@test.org')
        insert('student', **u2)
        r=Student.get(name='Ma')
        self.assertEqual(2, r[0].id)

    def test_get_all(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Ma', email='2@test.org')
        insert('student', **u2)
        r=Student.get_all()
        self.assertEqual(2, len(r))

    def test_get_first(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Chao', email='2@test.org')
        insert('student', **u2)
        r = Student.get_first(name='Chao')
        self.assertEqual(1, r.id)

    def test_count(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Chao', email='2@test.org')
        insert('student', **u2)
        r=Student.count(name='Chao')
        self.assertEqual(2,r)
        r = Student.count(email='1@test.org')
        self.assertEqual(1, r)

    def test_count_all(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Chao', email='2@test.org')
        insert('student', **u2)
        r = Student.count_all()
        self.assertEqual(2, r)

    def test_update_all(self):
        s = Student()
        u1 = dict(id=1, name='Chao', email='1@test.org')
        insert('student', **u1)
        u2 = dict(id=2, name='Ma', email='2@test.org')
        insert('student', **u2)
        r=s.get_by_pk(2)
        s2 = Student(**r)
        s2.name='k'
        s2.update_all()
        r2=s.get_by_pk(2)
        self.assertEqual('k', r2.name)

    def test_insert(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        s = Student(**u1)
        s.insert()
        r = s.get_by_pk(1)
        self.assertEqual('1@test.org', r.email)

    def test_delete(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        s = Student(**u1)
        s.insert()
        r = s.get_by_pk(1)
        self.assertEqual('1@test.org', r.email)
        s.delete()
        r = Student.get_all()
        self.assertEqual(0, len(r))

    def test_delete_by_pk(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        s = Student(**u1)
        s.insert()
        Student.delete_by_pk(1)
        r = Student.get_all()
        self.assertEqual(0, len(r))

    def test_delete_by_attr(self):
        u1 = dict(id=1, name='Chao', email='1@test.org')
        s = Student(**u1)
        s.insert()
        Student.delete_by_attr(name='Chao')
        r = Student.get_all()
        self.assertEqual(0, len(r))

