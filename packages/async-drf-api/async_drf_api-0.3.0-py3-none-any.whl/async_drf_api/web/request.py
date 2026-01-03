import json

class Request:
    def __init__(self, starlette_request):
        self._request = starlette_request
        self._json = None
    
    @property
    def method(self):
        return self._request.method
    
    @property
    def url(self):
        return self._request.url
    
    @property
    def path(self):
        return self._request.url.path
    
    @property
    def headers(self):
        return self._request.headers
    
    @property
    def query_params(self):
        return dict(self._request.query_params)
    
    @property
    def path_params(self):
        return self._request.path_params
    
    async def json(self):
        if self._json is None:
            body = await self._request.body()
            if body:
                self._json = json.loads(body)
            else:
                self._json = {}
        return self._json
    
    async def body(self):
        return await self._request.body()
    
    async def form(self):
        form = await self._request.form()
        return dict(form)
    
    async def files(self):
        form = await self._request.form()
        return dict(form)
    
    def __getitem__(self, key):
        return self.path_params[key]

