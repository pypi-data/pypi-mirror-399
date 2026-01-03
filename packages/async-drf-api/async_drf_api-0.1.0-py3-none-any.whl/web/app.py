from starlette.applications import Starlette
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from starlette.routing import Route

class AsyncDrfApiApp:
    def __init__(self, middleware=None, docs=True, title="API"):
        self.middleware = middleware or []
        self.routes = []
        self.starlette_app = None
        self.docs = docs
        self.docs_title = title
        self._route_info = []  # 保存路由信息
        self._schema = None  # 保存 OpenAPI Schema
        self._router = None  # 路由注册器
        self._startup_handlers = []  # Starlette startup 事件处理器
        self._shutdown_handlers = []  # Starlette shutdown 事件处理器

        # 如果可用，自动为 ORM 注册默认的数据库连接 / 关闭钩子
        try:
            from async_drf_api.orm.connection import Database
        except ImportError:
            Database = None

        if Database is not None:
            async def _db_startup():
                db = Database()
                await db.connect()

            async def _db_shutdown():
                db = Database()
                await db.close()

            # 默认注册到生命周期事件中（用户也可以在应用层覆写 / 追加）
            self.on_startup(_db_startup)
            self.on_shutdown(_db_shutdown)
        
    def add_route(self, path, view_func, methods=None, **kwargs):
        if methods is None:
            methods = ['GET']
        elif isinstance(methods, str):
            methods = [methods]
        
        # 保存路由信息用于文档生成
        if self.docs:
            self._route_info.append({
                'path': path,
                'methods': methods,
                'func': view_func
            })
        
        async def starlette_handler(request):
            starlette_request = request
            response = await view_func(starlette_request)
            return response
            
        self.routes.append(Route(path, starlette_handler, methods=methods))
    
    def get(self, path):
        def decorator(view_func):
            self.add_route(path, view_func, methods=['GET'])
            return view_func
        return decorator
    
    def post(self, path):
        def decorator(view_func):
            self.add_route(path, view_func, methods=['POST'])
            return view_func
        return decorator
    
    def put(self, path):
        def decorator(view_func):
            self.add_route(path, view_func, methods=['PUT'])
            return view_func
        return decorator
    
    def delete(self, path):
        def decorator(view_func):
            self.add_route(path, view_func, methods=['DELETE'])
            return view_func
        return decorator
    
    def patch(self, path):
        def decorator(view_func):
            self.add_route(path, view_func, methods=['PATCH'])
            return view_func
        return decorator
    
    def _get_starlette_app(self):
        if self.starlette_app is None:
            from starlette.middleware import Middleware
            from starlette.middleware.cors import CORSMiddleware
            
            middleware = [Middleware(CORSMiddleware, allow_origins=["*"])]
            middleware.extend([Middleware(mw) for mw in self.middleware])
            
            if self.docs:
                try:
                    from async_drf_api.docs.openapi import OpenAPISchema, get_swagger_ui_html, get_redoc_html
                    from starlette.responses import HTMLResponse, JSONResponse
                    
                    schema = OpenAPISchema(title=self.docs_title)
                    
                    # 从保存的路由信息中提取并生成 OpenAPI Schema
                    for route_info in self._route_info:
                        path = route_info['path']
                        methods = route_info['methods']
                        func = route_info['func']
                        
                        # 获取函数的文档字符串
                        summary = ""
                        description = ""
                        if hasattr(func, '__doc__') and func.__doc__:
                            doc_lines = func.__doc__.strip().split('\n')
                            summary = doc_lines[0] if doc_lines else ""
                            description = '\n'.join(doc_lines[1:]) if len(doc_lines) > 1 else ""
                        
                        for method in methods:
                            method_upper = method.upper()
                            
                            # 为 GET 请求添加基础响应
                            if method_upper == 'GET':
                                schema.add_path(path, method_upper, summary=summary, description=description)
                            # 为 POST/PUT/PATCH 请求添加请求体
                            elif method_upper in ['POST', 'PUT', 'PATCH']:
                                schema.add_path(path, method_upper, 
                                               summary=summary, 
                                               description=description,
                                               request_body={
                                                   "content": {
                                                       "application/json": {
                                                           "schema": {
                                                               "type": "object"
                                                           }
                                                       }
                                                   }
                                               })
                            # 为 DELETE 请求添加 204 响应
                            elif method_upper == 'DELETE':
                                schema.add_path(path, method_upper, 
                                               summary=summary, 
                                               description=description,
                                               responses={
                                                   "204": {
                                                       "description": "No content"
                                                   }
                                               })
                    
                    # 保存 schema 以便在闭包中使用
                    self._schema = schema
                    
                    # Add route for docs
                    async def docs_handler(request):
                        return HTMLResponse(content=get_swagger_ui_html())
                    
                    async def redoc_handler(request):
                        return HTMLResponse(content=get_redoc_html())
                    
                    async def schema_handler(request):
                        return JSONResponse(self._schema.get_schema())
                    
                    docs_route = Route('/docs', docs_handler, methods=['GET'])
                    redoc_route = Route('/redoc', redoc_handler, methods=['GET'])
                    schema_route = Route('/openapi.json', schema_handler, methods=['GET'])
                    
                    self.routes.extend([docs_route, redoc_route, schema_route])
                except ImportError:
                    pass
            
            self.starlette_app = Starlette(routes=self.routes, middleware=middleware)

            # 注册用户自定义的 startup / shutdown 事件处理器
            if self._startup_handlers:
                for handler in self._startup_handlers:
                    self.starlette_app.add_event_handler("startup", handler)
            if self._shutdown_handlers:
                for handler in self._shutdown_handlers:
                    self.starlette_app.add_event_handler("shutdown", handler)
        return self.starlette_app
    
    async def __call__(self, scope, receive, send):
        app = self._get_starlette_app()
        return await app(scope, receive, send)

    def on_startup(self, func):
        """注册在 Starlette 应用启动时执行的异步函数"""
        self._startup_handlers.append(func)
        return func
    
    def on_shutdown(self, func):
        """注册在 Starlette 应用关闭时执行的异步函数"""
        self._shutdown_handlers.append(func)
        return func
    
    def set_router(self, router):
        """设置路由器，自动注册 ViewSet"""
        self._router = router
        # 将路由器的路由添加到应用中
        if router:
            for route in router.get_routes():
                self.routes.append(route)
            # 同步写入文档信息，确保 /docs 能显示由 ViewSet 注册的路由
            if self.docs:
                try:
                    for item in router.registered_viewsets:
                        prefix = item['prefix']
                        viewset = item['viewset']

                        # 将注释来源统一指向 ViewSet 类本身（用于 Swagger 注释）
                        doc_source = viewset.__class__

                        # 列表路径: GET, POST
                        list_methods = ['GET', 'POST']
                        self._route_info.append({
                            'path': prefix,
                            'methods': list_methods,
                            'func': doc_source
                        })

                        # 详情路径: GET, PUT, PATCH, DELETE
                        detail_path = f"{prefix}/{{id}}"
                        detail_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
                        self._route_info.append({
                            'path': detail_path,
                            'methods': detail_methods,
                            'func': doc_source
                        })
                except Exception:
                    # 文档生成失败不影响路由注册
                    pass
    
    def run(self, host='127.0.0.1', port=8000, debug=False, reload=False):
        import uvicorn
        uvicorn.run(self, host=host, port=port, log_level='debug' if debug else 'info', reload=reload)
