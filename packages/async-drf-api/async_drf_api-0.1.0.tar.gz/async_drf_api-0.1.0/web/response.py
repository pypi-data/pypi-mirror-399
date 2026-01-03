import json

class Response:
    def __init__(self, content, status_code=200, headers=None, content_type='application/json'):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.content_type = content_type
    
    async def __call__(self, scope, receive, send):
        from starlette.responses import JSONResponse, HTMLResponse
        
        if isinstance(self.content, str):
            response = HTMLResponse(content=self.content, status_code=self.status_code, headers=self.headers)
        elif isinstance(self.content, dict):
            response = JSONResponse(content=self.content, status_code=self.status_code, headers=self.headers)
        else:
            response = JSONResponse(content={'data': self.content}, status_code=self.status_code, headers=self.headers)
        
        return await response(scope, receive, send)

