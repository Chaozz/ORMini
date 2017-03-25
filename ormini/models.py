from fields import *
from utils import *
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
        primary_key=None
        fields=dict()
        # if table name not defined, set as the name of the class
        if '__name__' not in attrs:
            attrs['__name__']=name.lower()
        for k, v in attrs.items():
            if isinstance(v, Field):
                # if not specified, set field attribute name as field name,
                if v.name is None:
                    v.name=k
                # check duplicate primary key
                if v.primary_key:
                    if primary_key:
                        raise ModelError("duplicate primary keys!")
                    v.editable=False
                    v.not_null=True
                    primary_key=v
                fields[k]=v
                # delete fields from attributes
                attrs.pop(k)
        # if there is no primary_key, add an autoField
        if not primary_key:
            if 'id' not in attrs:
                fields['id']=AutoPrimaryKeyField()
            else:
                raise ModelError('Primary key not defined!')
        attrs['__primary_key__']=primary_key
        attrs['__fields__']=fields
        return type.__new__(cls, name, bases, attrs)


class Model(Dict):
    """Base Model class represent table in Database"""
    __metaclass__ = ModelMetaClass

    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def create_table_sql(self):
        """generate create table SQL"""
        sql=['create table `%s` (\n' % self.__name__]
        for field in self.__fields__.values():
            if isinstance(field, CharField):
                sql.append('%s varchar(%d)' % (field.name, field.max_length))
            else:
                sql.append('%s %s' % (field.name, field.data_type))
            if field.not_null:
                sql.append(' NOT NULL')
            sql.append(',\n')
        sql.append('  primary key( %s )\n' % self.__primary_key__.name)
        sql.append(');')
        return ''.join(sql)

    def create_table(self):
        db.update(self.create_table_sql())








