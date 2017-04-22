class NOT_PROVIDED:
    pass


def check(value):
    """Generate SQL of check constraints """

    return 'CHECK (%s)' % value


class Field(object):
    # Relation Flags
    many_to_many = None
    many_to_one = None
    one_to_many = None
    one_to_one = None

    def __init__(self, name=None, primary_key=False,
                 max_length=None, unique=False, not_null=False, data_type=None,
                 default=NOT_PROVIDED, editable=True, choices=None, validators=(),
                 db_index=False, constraints=[]):
        self.name = name
        self.primary_key = primary_key
        self.max_length = max_length
        self.unique = unique
        self.not_null = not_null
        self.data_type = data_type
        self.default = default
        self.editable = editable
        self.choices = choices
        self.validators = list(validators)
        self.db_index = db_index
        # https://dev.mysql.com/doc/refman/5.7/en/create-table.html
        # The CHECK clause is parsed but ignored by MySQL
        self.constraints = []


class BooleanField(Field):
    def __init__(self, **kwargs):
        kwargs['data_type'] = 'bool'
        kwargs['not_null'] = True
        if 'default' not in kwargs:
            kwargs['default'] = False
        super(BooleanField, self).__init__(**kwargs)


class CharField(Field):
    def __init__(self, **kwargs):
        kwargs['data_type'] = 'varchar'
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 255
        if 'default' not in kwargs:
            kwargs['default'] = ''
        super(CharField, self).__init__(**kwargs)


class IntegerField(Field):
    def __init__(self, **kwargs):
        kwargs['data_type'] = 'int'
        if 'default' not in kwargs:
            kwargs['default'] = 0
        super(IntegerField, self).__init__(**kwargs)


class FloatField(Field):
    def __init__(self, **kwargs):
        kwargs['data_type'] = 'real'
        if 'default' not in kwargs:
            kwargs['default'] = 0
        super(FloatField, self).__init__(**kwargs)


class TextField(Field):
    def __init__(self, **kwargs):
        kwargs['data_type'] = 'text'
        if 'default' not in kwargs:
            kwargs['default'] = ''
        super(TextField, self).__init__(**kwargs)


class AutoPrimaryKeyField(Field):
    def __init__(self, **kwargs):
        kwargs['primary_key'] = True
        kwargs['data_type'] = 'int'
        if 'name' not in kwargs:
            kwargs['name'] = 'id'
        if 'default' not in kwargs:
            kwargs['default'] = 0
        super(AutoPrimaryKeyField, self).__init__(**kwargs)


class ForeignKeyField(IntegerField):
    def __init__(self, related_model, related_field,
                 on_delete=None, on_update=None, **kwargs):
        from models import Model
        # check if related_model is valid
        if related_model!= 'self' and not issubclass(related_model, Model):
            raise TypeError("related_model must refer to a Model name!")
        self.related_model = related_model
        self.related_field = related_field
        self.on_delete = on_delete
        self.on_update = on_update
        super(ForeignKeyField, self).__init__(**kwargs)
