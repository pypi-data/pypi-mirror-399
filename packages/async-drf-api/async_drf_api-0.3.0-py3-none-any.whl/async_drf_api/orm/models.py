from .connection import Database
from .query import QuerySet
from .field import Field

class DoesNotExist(Exception):
    pass


class ObjectsDescriptor:
    """描述符，使 Model.objects 作为属性访问"""
    def __get__(self, instance, owner):
        return QuerySet(owner)


class Model:
    objects = ObjectsDescriptor()
    DoesNotExist = DoesNotExist
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        if not hasattr(self.__class__, '_meta'):
            self.__class__._meta = type('Meta', (), {
                'table_name': self.__class__.__name__.lower() + 's',
                'abstract': False
            })()
        
        if hasattr(self.__class__, 'Meta'):
            if hasattr(self.__class__.Meta, 'table_name'):
                self.__class__._meta.table_name = self.__class__.Meta.table_name
    
    @classmethod
    def _get_fields(cls):
        fields = {}
        for name, obj in cls.__dict__.items():
            if isinstance(obj, Field):
                fields[name] = obj
        return fields
    
    @classmethod
    async def create_table(cls):
        if not hasattr(cls, '_meta'):
            cls._meta = type('Meta', (), {
                'table_name': cls.__name__.lower() + 's',
                'abstract': False
            })()
        
        if hasattr(cls, 'Meta'):
            if hasattr(cls.Meta, 'table_name'):
                cls._meta.table_name = cls.Meta.table_name
        
        fields = cls._get_fields()
        field_defs = []
        for name, field in fields.items():
            field_def = '{} {}'.format(name, field.field_type)
            if field.primary_key:
                field_def += ' PRIMARY KEY'
            if not field.null and not field.primary_key:
                field_def += ' NOT NULL'
            if field.unique:
                field_def += ' UNIQUE'
            field_defs.append(field_def)
        
        create_table_sql = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(
            cls._meta.table_name,
            ', '.join(field_defs)
        )
        db = Database()
        await db.execute(create_table_sql)
    
    @classmethod
    def _get_or_create_meta(cls):
        if not hasattr(cls, '_meta'):
            cls._meta = type('Meta', (), {
                'table_name': cls.__name__.lower() + 's',
                'abstract': False
            })()
        return cls._meta
    
    async def save(self):
        db = Database()
        fields = self.__class__._get_fields()
        pk_field = None
        pk_value = None
        
        for name, field in fields.items():
            if field.primary_key:
                pk_field = name
                pk_value = getattr(self, name, None)
                break
        
        values = {}
        for name, field in fields.items():
            value = getattr(self, name, field.default)
            if value is not None:
                values[name] = value
        
        if pk_value is not None:
            set_clauses = ', '.join(['{} = ?'.format(k) for k in values.keys() if k != pk_field])
            update_sql = 'UPDATE {} SET {} WHERE {} = ?'.format(
                self.__class__._meta.table_name,
                set_clauses,
                pk_field
            )
            await db.execute(update_sql, list(values.values()) + [pk_value])
        else:
            columns = ', '.join(values.keys())
            placeholders = ', '.join(['?' for _ in values])
            insert_sql = 'INSERT INTO {} ({}) VALUES ({})'.format(
                self.__class__._meta.table_name,
                columns,
                placeholders
            )
            cursor = await db.execute(insert_sql, list(values.values()))
            if pk_field:
                setattr(self, pk_field, cursor.lastrowid)
    
    async def delete(self):
        db = Database()
        fields = self.__class__._get_fields()
        pk_field = None
        pk_value = None
        
        for name, field in fields.items():
            if field.primary_key:
                pk_field = name
                pk_value = getattr(self, name)
                break
        
        if pk_field and pk_value is not None:
            delete_sql = 'DELETE FROM {} WHERE {} = ?'.format(
                self.__class__._meta.table_name,
                pk_field
            )
            await db.execute(delete_sql, [pk_value])
    
    @classmethod
    async def create(cls, **kwargs):
        instance = cls(**kwargs)
        await instance.save()
        return instance
    
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.__dict__)

# Set DoesNotExist on the Model class for backwards compatibility
Model.DoesNotExist = DoesNotExist

