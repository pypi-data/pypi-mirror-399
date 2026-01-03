# Async DRF API

一个基于 Starlette 的异步 Web API 框架，灵感来自 Django REST Framework，提供简洁的 API 开发体验。
仓库链接：https://github.com/sixsfish/async_drf_api
## 功能特性

- 🚀 **异步支持** - 基于 Starlette 和 asyncio，支持高并发
- 📝 **自动 API 文档** - 自动生成 Swagger UI 和 ReDoc 文档
- 🗄️ **异步 ORM** - 内置异步数据库操作（支持 SQLite）
- 🔄 **序列化器** - 类似 DRF 的数据序列化/反序列化
- 🎯 **视图集** - 支持 ViewSet 和通用视图
- 🛣️ **路由装饰器** - 简洁的路由定义方式
- 🔌 **中间件支持** - 灵活的中间件机制

## 安装

```bash
pip install async-drf-api
```

## 快速开始

### 1. 创建应用

```python
from async_drf_api.web.app import AsyncDrfApiApp
from async_drf_api.web.response import Response

app = AsyncDrfApiApp()

@app.get('/')
async def home(request):
    return Response({'message': 'Hello, Async DRF API!'})

@app.post('/api/users')
async def create_user(request):
    data = await request.json()
    # 处理数据...
    return Response({'id': 1, 'name': data.get('name')}, status_code=201)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 2. 使用 ORM 模型

```python
from async_drf_api.orm.models import Model
from async_drf_api.orm.field import CharField, IntegerField
from async_drf_api.orm.connection import Database

# 定义模型
class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()
    
    class Meta:
        table_name = 'users'

# 配置数据库
from async_drf_api.conf import get_settings
settings = get_settings()
settings.DATABASE_NAME = 'myapp.db'

# 创建表
await User.create_table()

# 使用模型
user = await User.objects.create(name='Alice', age=30)
users = await User.objects.all()
user = await User.objects.get(id=1)
await user.update(name='Bob')
await user.delete()
```

### 3. 使用序列化器

```python
from async_drf_api.serializers import Serializer

class UserSerializer(Serializer):
    name = CharField()
    age = IntegerField()
    
    def validate_age(self, value):
        if value < 0:
            raise ValueError('Age must be positive')
        return value

# 序列化
user = User(name='Alice', age=30)
serializer = UserSerializer(user)
data = serializer.data  # {'name': 'Alice', 'age': 30}

# 反序列化
data = {'name': 'Bob', 'age': 25}
serializer = UserSerializer(data=data)
if serializer.is_valid():
    validated_data = serializer.validated_data
```

### 4. 使用 ViewSet 和 Router

```python
from async_drf_api.views.generic import GenericAPIView
from async_drf_api.views.router import SimpleRouter

class UserViewSet(GenericAPIView):
    queryset = User.objects
    serializer_class = UserSerializer

# 注册路由
router = SimpleRouter()
router.register('/api/users', UserViewSet)
app.set_router(router)
```

### 5. 生命周期事件

```python
@app.on_startup
async def startup():
    """应用启动时执行"""
    print('Application starting...')
    # 初始化数据库连接等

@app.on_shutdown
async def shutdown():
    """应用关闭时执行"""
    print('Application shutting down...')
    # 清理资源等
```

## API 文档

启动应用后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

## 完整示例

```python
import asyncio
from async_drf_api.web.app import AsyncDrfApiApp
from async_drf_api.web.response import Response
from async_drf_api.orm.models import Model
from async_drf_api.orm.field import CharField, IntegerField
from async_drf_api.orm.connection import Database
from async_drf_api.serializers import Serializer, CharField as SerializerCharField, IntegerField as SerializerIntegerField
from async_drf_api.views.generic import GenericAPIView
from async_drf_api.views.router import SimpleRouter
from async_drf_api.conf import get_settings

# 配置数据库
settings = get_settings()
settings.DATABASE_NAME = 'example.db'

# 定义模型
class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()
    
    class Meta:
        table_name = 'users'

# 定义序列化器
class UserSerializer(Serializer):
    name = SerializerCharField()
    age = SerializerIntegerField()

# 定义视图集
class UserViewSet(GenericAPIView):
    queryset = User.objects
    serializer_class = UserSerializer

# 创建应用
app = AsyncDrfApiApp(title="Example API")

# 注册路由
router = SimpleRouter()
router.register('/api/users', UserViewSet)
app.set_router(router)

# 添加自定义路由
@app.get('/api/health')
async def health_check(request):
    return Response({'status': 'ok'})

```

启动应用：uvicorn main:app --port=8000
## 依赖

- `starlette` - Web 框架
- `uvicorn` - ASGI 服务器


---

# Async DRF API---ENGLISH

An asynchronous Web API framework based on Starlette, inspired by Django REST Framework, providing a clean API development experience.
Repository: https://github.com/sixsfish/async_drf_api

## Features

- 🚀 **Async Support** - Based on Starlette and asyncio, supports high concurrency
- 📝 **Auto API Documentation** - Automatically generates Swagger UI and ReDoc documentation
- 🗄️ **Async ORM** - Built-in asynchronous database operations (supports SQLite)
- 🔄 **Serializers** - Data serialization/deserialization similar to DRF
- 🎯 **ViewSets** - Supports ViewSet and generic views
- 🛣️ **Route Decorators** - Clean route definition
- 🔌 **Middleware Support** - Flexible middleware mechanism

## Installation

```bash
pip install async-drf-api
```

## Quick Start

### 1. Create Application

```python
from async_drf_api.web.app import AsyncDrfApiApp
from async_drf_api.web.response import Response

app = AsyncDrfApiApp()

@app.get('/')
async def home(request):
    return Response({'message': 'Hello, Async DRF API!'})

@app.post('/api/users')
async def create_user(request):
    data = await request.json()
    # Process data...
    return Response({'id': 1, 'name': data.get('name')}, status_code=201)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 2. Use ORM Models

```python
from async_drf_api.orm.models import Model
from async_drf_api.orm.field import CharField, IntegerField
from async_drf_api.orm.connection import Database

# Define model
class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()
    
    class Meta:
        table_name = 'users'

# Configure database
from async_drf_api.conf import get_settings
settings = get_settings()
settings.DATABASE_NAME = 'myapp.db'

# Create table
await User.create_table()

# Use model
user = await User.objects.create(name='Alice', age=30)
users = await User.objects.all()
user = await User.objects.get(id=1)
await user.update(name='Bob')
await user.delete()
```

### 3. Use Serializers

```python
from async_drf_api.serializers import Serializer

class UserSerializer(Serializer):
    name = CharField()
    age = IntegerField()
    
    def validate_age(self, value):
        if value < 0:
            raise ValueError('Age must be positive')
        return value

# Serialize
user = User(name='Alice', age=30)
serializer = UserSerializer(user)
data = serializer.data  # {'name': 'Alice', 'age': 30}

# Deserialize
data = {'name': 'Bob', 'age': 25}
serializer = UserSerializer(data=data)
if serializer.is_valid():
    validated_data = serializer.validated_data
```

### 4. Use ViewSets and Router

```python
from async_drf_api.views.generic import GenericAPIView
from async_drf_api.views.router import SimpleRouter

class UserViewSet(GenericAPIView):
    queryset = User.objects
    serializer_class = UserSerializer

# Register routes
router = SimpleRouter()
router.register('/api/users', UserViewSet)
app.set_router(router)
```

### 5. Lifecycle Events

```python
@app.on_startup
async def startup():
    """Execute on application startup"""
    print('Application starting...')
    # Initialize database connections, etc.

@app.on_shutdown
async def shutdown():
    """Execute on application shutdown"""
    print('Application shutting down...')
    # Clean up resources, etc.
```

## API Documentation

After starting the application, visit the following URLs to view auto-generated API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

## Complete Example

```python
import asyncio
from async_drf_api.web.app import AsyncDrfApiApp
from async_drf_api.web.response import Response
from async_drf_api.orm.models import Model
from async_drf_api.orm.field import CharField, IntegerField
from async_drf_api.orm.connection import Database
from async_drf_api.serializers import Serializer, CharField as SerializerCharField, IntegerField as SerializerIntegerField
from async_drf_api.views.generic import GenericAPIView
from async_drf_api.views.router import SimpleRouter
from async_drf_api.conf import get_settings

# Configure database
settings = get_settings()
settings.DATABASE_NAME = 'example.db'

# Define model
class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()
    
    class Meta:
        table_name = 'users'

# Define serializer
class UserSerializer(Serializer):
    name = SerializerCharField()
    age = SerializerIntegerField()

# Define viewset
class UserViewSet(GenericAPIView):
    queryset = User.objects
    serializer_class = UserSerializer

# Create application
app = AsyncDrfApiApp(title="Example API")

# Register routes
router = SimpleRouter()
router.register('/api/users', UserViewSet)
app.set_router(router)

# Add custom routes
@app.get('/api/health')
async def health_check(request):
    return Response({'status': 'ok'})

```
Run application：uvicorn main:app --port=8000
## Dependencies

- `starlette` - Web framework
- `uvicorn` - ASGI server

