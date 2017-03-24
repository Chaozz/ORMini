from unittest import TestCase
from ormini.db import *
from config import configs
import time


class DBTests(TestCase):
    @classmethod
    def setUpClass(cls):
        init_engine(**configs['testDB'])

    def setUp(self):
        update('drop table if exists user')
        update('create table user (id int primary key, name text, email text, passwd text, last_modified real)')

    def test_transaction(self):
        with TransactionContext():
            u = dict(id=123, name='Chao', email='111@test.org', passwd='pass', last_modified=time.time())
            insert('user', **u)
            update('update user set passwd=? where id=?', 'new_pass', 123)
        r = select_one('select * from user where id=?', 123)
        self.assertEqual('Chao', r.name)
        self.assertEqual('new_pass', r.passwd)
        r = select('select * from user where id=?', 124)
        self.assertEqual(0, len(r))

    def test_with_transaction(self):
        @with_transaction
        def update_profile(name1, name2):
            u1 = dict(id=1, name=name1, email='111@test.org', passwd=name1, last_modified=time.time())
            insert('user', **u1)
            u2 = dict(id=2, name=name2, email='111@test.org', passwd=name2, last_modified=time.time())
            insert('user', **u2)

        update_profile('Chao', 'Ma')
        r = select_one('select * from user where name=?', 'Chao').passwd
        self.assertEqual('Chao', r)
        r = select('select * from user where name=?', 'Ma')
        self.assertEqual('Ma', r[0].passwd)

    def test_select_one(self):
        u1 = dict(id=1, name='Chao', email='111@test.org', passwd='pass1', last_modified=time.time())
        insert('user', **u1)
        u2 = dict(id=2, name='Ma', email='111@test.org', passwd='pass2', last_modified=time.time())
        insert('user', **u2)
        r = select_one('select * from user where name=?', 'Chao').passwd
        self.assertEqual('pass1', r)
        r = select_one('select * from user where name=?', 'Ma')
        self.assertEqual('pass2', r.passwd)

    def test_select_int(self):
        u1 = dict(id=1, name='Chao', email='111@test.org', passwd='pass1', last_modified=time.time())
        insert('user', **u1)
        u2 = dict(id=2, name='Ma', email='111@test.org', passwd='pass2', last_modified=time.time())
        insert('user', **u2)
        r = select_int('select count(*) from user where name=?', 'Chao')
        self.assertEqual(1, r)
        r = select_int('select count(*) from user')
        self.assertEqual(2, r)

    def test_select(self):
        u1 = dict(id=1, name='Chao', email='111@test.org', passwd='pass1', last_modified=time.time())
        insert('user', **u1)
        u2 = dict(id=2, name='Ma', email='111@test.org', passwd='pass2', last_modified=time.time())
        insert('user', **u2)
        r = select('select * from user')
        self.assertEqual('Chao', r[0].name)
        self.assertEqual('Ma', r[1].name)

    def test_insert(self):
        u1 = dict(id=1, name='Chao', email='111@test.org', passwd='pass1', last_modified=time.time())
        insert('user', **u1)
        r = select('select * from user')
        self.assertEqual('Chao', r[0].name)
        u2 = dict(id=1, name='Chao', email='111@test.org', passwd='pass1', last_modified=time.time())
        self.assertRaises(Exception, lambda: insert('user', **u2))

    def test_update(self):
        u1 = dict(id=1, name='Chao', email='111@test.org', passwd='pass1', last_modified=time.time())
        insert('user', **u1)
        update('update user set passwd=? where id=?', 'newpass', 1)
        r = select('select * from user')
        self.assertEqual('newpass', r[0].passwd)
