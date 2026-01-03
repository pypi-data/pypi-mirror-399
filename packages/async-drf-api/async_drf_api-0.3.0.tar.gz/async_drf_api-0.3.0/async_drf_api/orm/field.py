class Field:
    def __init__(self, field_type, primary_key=False, null=True, default=None, unique=False):
        self.field_type = field_type
        self.primary_key = primary_key
        self.null = null
        self.default = default
        self.unique = unique

class CharField(Field):
    def __init__(self, max_length=255, **kwargs):
        super().__init__('VARCHAR({})'.format(max_length), **kwargs)
        self.max_length = max_length

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__('INTEGER', **kwargs)

class FloatField(Field):
    def __init__(self, **kwargs):
        super().__init__('REAL', **kwargs)

class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__('BOOLEAN', **kwargs)

class DateTimeField(Field):
    def __init__(self, **kwargs):
        super().__init__('DATETIME', **kwargs)

class TextField(Field):
    def __init__(self, **kwargs):
        super().__init__('TEXT', **kwargs)

