class BaseMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            return await self.process_request(scope, receive, send)
        return await self.app(scope, receive, send)
    
    async def process_request(self, scope, receive, send):
        return await self.app(scope, receive, send)
    
    async def process_response(self, response):
        return response

