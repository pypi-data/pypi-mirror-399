from .connection import Database

class QuerySet:
    def __init__(self, model):
        self.model = model
        # 确保 model 有 _meta
        if not hasattr(model, '_meta'):
            model._meta = type('Meta', (), {
                'table_name': model.__name__.lower() + 's',
                'abstract': False
            })()
        
        if hasattr(model, 'Meta') and hasattr(model.Meta, 'table_name'):
            model._meta.table_name = model.Meta.table_name
        
        self.sql = 'SELECT * FROM {}'.format(model._meta.table_name)
        self.params = []
        self._limit = None
        self._offset = None
        self._order_by = []
    
    def filter(self, **kwargs):
        where_clauses = []
        where_params = []
        
        for key, value in kwargs.items():
            if '__' in key:
                field, operator = key.split('__', 1)
                if operator == 'in':
                    placeholders = ', '.join(['?' for _ in value])
                    where_clauses.append('{} IN ({})'.format(field, placeholders))
                    where_params.extend(value)
                elif operator == 'contains':
                    where_clauses.append('{} LIKE ?'.format(field))
                    where_params.append('%{}%'.format(value))
                elif operator == 'startswith':
                    where_clauses.append('{} LIKE ?'.format(field))
                    where_params.append('{}%'.format(value))
                elif operator == 'endswith':
                    where_clauses.append('{} LIKE ?'.format(field))
                    where_params.append('%{}'.format(value))
                elif operator == 'gt':
                    where_clauses.append('{} > ?'.format(field))
                    where_params.append(value)
                elif operator == 'gte':
                    where_clauses.append('{} >= ?'.format(field))
                    where_params.append(value)
                elif operator == 'lt':
                    where_clauses.append('{} < ?'.format(field))
                    where_params.append(value)
                elif operator == 'lte':
                    where_clauses.append('{} <= ?'.format(field))
                    where_params.append(value)
                else:
                    raise ValueError('Unknown operator: {}'.format(operator))
            else:
                where_clauses.append('{} = ?'.format(key))
                where_params.append(value)
        
        if where_clauses:
            if 'WHERE' not in self.sql:
                self.sql += ' WHERE ' + ' AND '.join(where_clauses)
            else:
                self.sql += ' AND ' + ' AND '.join(where_clauses)
            self.params.extend(where_params)
        
        return self
    
    def order_by(self, *fields):
        self._order_by.extend(fields)
        return self
    
    def limit(self, n):
        self._limit = n
        return self
    
    def offset(self, n):
        self._offset = n
        return self
    
    def _build_sql(self):
        sql = self.sql
        
        if self._order_by:
            sql += ' ORDER BY ' + ', '.join(self._order_by)
        
        if self._limit is not None:
            sql += ' LIMIT {}'.format(self._limit)
        
        if self._offset is not None:
            sql += ' OFFSET {}'.format(self._offset)
        
        return sql
    
    async def all(self):
        db = Database()
        sql = self._build_sql()
        rows = await db.fetch(sql, self.params)
        return [self.model(**row) for row in rows]
    
    async def get(self, **kwargs):
        self.filter(**kwargs)
        db = Database()
        sql = self._build_sql()
        row = await db.fetchone(sql, self.params)
        if not row:
            raise self.model.DoesNotExist('Object not found')
        return self.model(**row)
    
    async def first(self):
        db = Database()
        sql = self._build_sql()
        sql += ' LIMIT 1'
        row = await db.fetchone(sql, self.params)
        if not row:
            return None
        return self.model(**row)
    
    async def count(self):
        db = Database()
        count_sql = 'SELECT COUNT(*) as count FROM {}'.format(self.model._meta.table_name)
        
        if self.params:
            where_index = count_sql.find('FROM')
            if 'WHERE' in self.sql:
                where_clause = self.sql[self.sql.find('WHERE'):]
                count_sql += ' ' + where_clause
        
        result = await db.fetchone(count_sql, self.params)
        return result['count']
    
    async def delete(self):
        db = Database()
        delete_sql = 'DELETE FROM {}'.format(self.model._meta.table_name)
        
        if self.params:
            if 'WHERE' in self.sql:
                where_clause = self.sql[self.sql.find('WHERE'):]
                delete_sql += ' ' + where_clause
        
        await db.execute(delete_sql, self.params)
    
    async def update(self, **kwargs):
        db = Database()
        set_clauses = ', '.join(['{} = ?'.format(k) for k in kwargs.keys()])
        update_sql = 'UPDATE {} SET {}'.format(self.model._meta.table_name, set_clauses)
        
        if self.params:
            if 'WHERE' in self.sql:
                where_clause = self.sql[self.sql.find('WHERE'):]
                update_sql += ' ' + where_clause
        
        await db.execute(update_sql, list(kwargs.values()) + self.params)

# DoesNotExist exception is defined in models.py

