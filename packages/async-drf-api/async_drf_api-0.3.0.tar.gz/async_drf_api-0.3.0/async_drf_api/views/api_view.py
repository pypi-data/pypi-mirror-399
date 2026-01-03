from ..web.request import Request
from ..web.response import Response

class APIView:
    async def dispatch(self, request):
        method_name = request.method.lower()
        handler = getattr(self, method_name, self.http_method_not_allowed)
        return await handler(request)
    
    async def http_method_not_allowed(self, request):
        return Response({'error': 'Method not allowed'}, status_code=405)
    
    async def __call__(self, starlette_request):
        request = Request(starlette_request)
        return await self.dispatch(request)
    
    async def get(self, request):
        raise NotImplementedError('You must implement get method')
    
    async def post(self, request):
        raise NotImplementedError('You must implement post method')
    
    async def put(self, request):
        raise NotImplementedError('You must implement put method')
    
    async def patch(self, request):
        raise NotImplementedError('You must implement patch method')
    
    async def delete(self, request):
        raise NotImplementedError('You must implement delete method')

