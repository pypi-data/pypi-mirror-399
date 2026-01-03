from ..web.app import ASyncDrfApiApp
from starlette.routing import Route

class SimpleRouter:
    def __init__(self):
        self.registered_viewsets = []
    
    def register(self, prefix, viewset_class, basename=None):
        # 确保 prefix 以 '/' 开头
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        
        basename = basename or viewset_class.__name__.lower().replace('viewset', '')
        viewset_instance = viewset_class()
        
        self.registered_viewsets.append({
            'prefix': prefix,
            'viewset': viewset_instance,
            'basename': basename
        })
        
        return {
            'prefix': prefix,
            'viewset': viewset_instance,
            'basename': basename
        }
    
    def get_routes(self):
        routes = []
        
        for item in self.registered_viewsets:
            prefix = item['prefix']
            viewset = item['viewset']
            
            # 创建闭包来捕获当前的 viewset 实例
            def make_handler(vs):
                async def handler(request):
                    from ..web.request import Request
                    req = Request(request)
                    return await vs.dispatch(req)
                return handler
            
            list_create_handler = make_handler(viewset)
            detail_handler = make_handler(viewset)
            
            routes.append(Route(prefix, list_create_handler, methods=['GET', 'POST']))
            routes.append(Route(f'{prefix}/{{id}}', detail_handler, methods=['GET', 'PUT', 'PATCH', 'DELETE']))
        
        return routes

