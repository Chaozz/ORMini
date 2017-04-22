from fields import Field, AutoPrimaryKeyField, CharField
from utils import Dict
import db


class ModelError(Exception):
    pass


class ModelMetaClass(type):
    """Metaclass for all models."""

    def __new__(cls, name, bases, attrs):
        # Make sure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelMetaClass)]
        if not parents:
            return type.__new__(cls, name, bases, attrs)
        primary_key = None
        fields = dict()
        # if table name not defined, set as the name of the class
        if '__table_name__' not in attrs:
            attrs['__table_name__'] = name.lower()
        for k, v in attrs.items():
            if isinstance(v, Field):
                # if not specified, set field attribute name as field name,
                if v.name is None:
                    v.name = k
                # check duplicate primary key
                if v.primary_key:
                    if primary_key:
                        raise ModelError("duplicate primary keys!")
                    v.editable = False
                    v.not_null = True
                    primary_key = v
                fields[k] = v
                # delete fields from attributes
                attrs.pop(k)
        # if there is no primary_key, add an autoField
        if not primary_key:
            if 'id' not in attrs:
                fields['id'] = AutoPrimaryKeyField()
            else:
                raise ModelError('Primary key not defined!')
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        return type.__new__(cls, name, bases, attrs)


class Model(Dict):
    """Base Model class represent table in Database"""
    __metaclass__ = ModelMetaClass

    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    @classmethod
    def create_table_sql(cls):
        """generate create table SQL"""
        sql = ['create table `%s` (\n' % cls.__table_name__]
        for field in cls.__fields__.values():
            if isinstance(field, CharField):
                sql.append('%s varchar(%d)' % (field.name, field.max_length))
            else:
                sql.append('%s %s' % (field.name, field.data_type))
            if field.not_null:
                sql.append(' NOT NULL')
            sql.append(',\n')
        sql.append('  primary key( %s )\n' % cls.__primary_key__.name)
        sql.append(');')
        return ''.join(sql)

    @classmethod
    def create_table(cls):
        db.update(cls.create_table_sql())
        cls.create_index()
        cls.create_check()

    @classmethod
    def create_index_sql(cls):
        sql = []
        sql_create_index = "CREATE INDEX %(name)s ON %(table)s (%(columns)s);"
        for field in cls.__fields__.values():
            # if we have a index on field
            if field.db_index:
                sql.append(sql_create_index % {
                    "name": "idx_" + field.name,
                    "table": cls.__table_name__,
                    "columns": field.name
                })
        return sql

    @classmethod
    def create_index(cls):
        for sql in cls.create_index_sql():
            db.update(sql)

    @classmethod
    def create_check_sql(cls):
        sql_create_check = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s CHECK (%(check)s)"
        sql = []
        for field in cls.__fields__.values():
            cnt = 0
            for constraint in field.constraints:
                cnt += 1
                sql.append(sql_create_check % {
                    "table": cls.__table_name__,
                    "name": "check_" + field.name + "_" + str(cnt),
                    "check": constraint
                })
        return sql

    @classmethod
    def create_check(cls):
        for sql in cls.create_check_sql():
            db.update(sql)

    @classmethod
    def get_by_pk(cls, pk):
        """Get by primary key"""
        sql = 'select * from %s where %s=?' % (cls.__table_name__, cls.__primary_key__.name)
        return cls(**db.select_one(sql, pk))

    @classmethod
    def get(cls, **kwargs):
        """Get by attribute"""
        if len(kwargs) != 1:
            raise TypeError("invalid number of attributes")
        sql = 'select * from %s where %s=?' % (cls.__table_name__, kwargs.keys()[0])
        return [cls(**r) for r in db.select(sql, kwargs.values()[0])]

    @classmethod
    def get_all(cls):
        """Get all tuples"""
        sql = 'select * from %s' % cls.__table_name__
        return [cls(**r) for r in db.select(sql)]

    @classmethod
    def get_first(cls, **kwargs):
        """Get by attribute, return only the first result"""
        if len(kwargs) != 1:
            raise TypeError("invalid number of attributes")
        sql = 'select * from %s where %s=?' % (cls.__table_name__, kwargs.keys()[0])
        return cls(**db.select_one(sql, kwargs.values()[0]))

    @classmethod
    def count(cls, **kwargs):
        """Count by attribute"""
        if len(kwargs) != 1:
            raise TypeError("invalid number of attributes")
        sql = 'select count(*) from %s where %s=?' % (cls.__table_name__, kwargs.keys()[0])
        return db.select_int(sql, kwargs.values()[0])

    @classmethod
    def count_all(cls):
        """Count by attribute"""
        sql = 'select count(*) from %s' % cls.__table_name__
        return db.select_int(sql)

    def update_all(self):
        """Update all attributes in the tuple"""
        L = []
        args = []
        for k, v in self.__fields__.items():
            if v.editable:
                if hasattr(self, k):
                    arg = getattr(self, k)
                else:
                    arg = v.default
                    setattr(self, k, arg)
                L.append('`%s`=?' % k)
                args.append(arg)
        pk = self.__primary_key__.name
        args.append(getattr(self, pk))
        db.update('update %s set %s where %s=?' % (self.__table_name__, ','.join(L), pk), *args)
        return self

    def insert(self):
        """Insert a tuple"""
        params = {}
        for k, v in self.__fields__.items():
            if not hasattr(self, k):
                setattr(self, k, v.default)
            params[v.name] = getattr(self, k)
        db.insert('%s' % self.__table_name__, **params)
        return self

    def delete(self):
        """Delete the object in table"""
        pk = self.__primary_key__.name
        args = (getattr(self, pk),)
        db.update('delete from %s where %s=?' % (self.__table_name__, pk), *args)
        return self

    @classmethod
    def delete_by_pk(cls, pk):
        """Delete by primary key"""
        db.update('delete from %s where %s=?' % (cls.__table_name__, cls.__primary_key__.name), pk)
        return

    @classmethod
    def delete_by_attr(cls, **kwargs):
        """Delete by attribute"""
        if len(kwargs) != 1:
            raise TypeError("invalid number of attributes")
        sql = 'delete from %s where %s=?' % (cls.__table_name__, kwargs.keys()[0])
        return db.update(sql, kwargs.values()[0])
