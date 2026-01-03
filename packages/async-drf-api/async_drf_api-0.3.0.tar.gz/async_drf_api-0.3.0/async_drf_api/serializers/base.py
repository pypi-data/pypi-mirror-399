class SerializerMetaclass(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        for key in fields.keys():
            attrs.pop(key)
        
        attrs['_fields'] = fields
        return super().__new__(cls, name, bases, attrs)

class Field:
    def __init__(self, required=True, default=None, allow_null=False, read_only=False, write_only=False):
        self.required = required
        self.default = default
        self.allow_null = allow_null
        self.read_only = read_only
        self.write_only = write_only

class CharField(Field):
    def __init__(self, max_length=None, min_length=None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length

class IntegerField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

class FloatField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

class BooleanField(Field):
    pass

class ListField(Field):
    def __init__(self, child=None, **kwargs):
        super().__init__(**kwargs)
        self.child = child

class DictField(Field):
    pass

class Serializer(metaclass=SerializerMetaclass):
    def __init__(self, instance=None, data=None, partial=False):
        self.instance = instance
        self.initial_data = data
        self.partial = partial
        self._errors = {}
        self._validated_data = {}
        self._fields = getattr(self.__class__, '_fields', {})
        
        if data is not None:
            self._validated_data = {}
            for key, field in self._fields.items():
                if field.write_only:
                    continue
                if key in data:
                    self._validated_data[key] = data[key]
                elif hasattr(instance, key):
                    self._validated_data[key] = getattr(instance, key)
        elif instance is not None:
            self._populate_from_instance()
    
    def _populate_from_instance(self):
        if hasattr(self.instance, '__dict__'):
            for key in self.instance.__dict__.keys():
                if key in self._fields:
                    self._validated_data[key] = getattr(self.instance, key)
    
    def is_valid(self):
        if self.initial_data is None:
            if self.instance is not None:
                return True
            return False
        
        self._errors = {}
        for key, field in self._fields.items():
            if field.read_only:
                continue
            
            value = self.initial_data.get(key, None)
            
            if value is None:
                if field.required and not self.partial:
                    self._errors[key] = 'This field is required'
                elif field.default is not None:
                    value = field.default
                elif not field.allow_null:
                    self._errors[key] = 'This field cannot be null'
                else:
                    self._validated_data[key] = value
                continue
            
            if hasattr(field, 'min_length') and field.min_length and len(str(value)) < field.min_length:
                self._errors[key] = 'Value is too short (minimum {})'.format(field.min_length)
            elif hasattr(field, 'max_length') and field.max_length and len(str(value)) > field.max_length:
                self._errors[key] = 'Value is too long (maximum {})'.format(field.max_length)
            elif hasattr(field, 'min_value') and field.min_value and value < field.min_value:
                self._errors[key] = 'Value is too small (minimum {})'.format(field.min_value)
            elif hasattr(field, 'max_value') and field.max_value and value > field.max_value:
                self._errors[key] = 'Value is too large (maximum {})'.format(field.max_value)
            else:
                self._validated_data[key] = value
        
        return len(self._errors) == 0
    
    @property
    def data(self):
        data = {}
        for key, field in self._fields.items():
            if field.write_only:
                continue
            if key in self._validated_data:
                data[key] = self._validated_data[key]
            elif hasattr(self, key):
                data[key] = getattr(self, key)
        return data
    
    @property
    def errors(self):
        return self._errors
    
    async def save(self):
        if self.instance is None:
            self.instance = self.Meta.model(**self._validated_data)
            await self.instance.save()
            return self.instance
        else:
            for key, value in self._validated_data.items():
                setattr(self.instance, key, value)
            await self.instance.save()
            return self.instance
    
    def validate(self, attrs):
        return attrs
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance
    
    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)

class SerializerWithMany(Serializer):
    def __init__(self, instances=None, data=None, many=False):
        self.many = many
        if many and instances is not None:
            super().__init__(data=data)
            self.instances = instances
        else:
            super().__init__(instances, data)
    
    @property
    def data(self):
        if self.many and hasattr(self, 'instances'):
            return [self.__class__(instance).data for instance in self.instances]
        return super().data

