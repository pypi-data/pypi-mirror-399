from .openapi import OpenAPISchema
import json

class DocumentationMiddleware:
    def __init__(self, app, schema):
        self.app = app
        self.schema = schema
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            path = scope['path']
            
            # Swagger UI
            if path == '/docs':
                from starlette.responses import HTMLResponse
                from .openapi import get_swagger_ui_html
                response = HTMLResponse(content=get_swagger_ui_html())
                await response(scope, receive, send)
                return
            
            # ReDoc
            if path == '/redoc':
                from starlette.responses import HTMLResponse
                from .openapi import get_redoc_html
                response = HTMLResponse(content=get_redoc_html())
                await response(scope, receive, send)
                return
            
            # OpenAPI JSON Schema
            if path == '/openapi.json':
                from starlette.responses import JSONResponse
                schema = self.schema.get_schema()
                response = JSONResponse(schema)
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)

