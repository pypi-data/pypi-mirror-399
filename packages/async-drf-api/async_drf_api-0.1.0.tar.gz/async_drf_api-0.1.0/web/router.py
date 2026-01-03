class Router:
    def __init__(self):
        self.routes = []
    
    def register(self, app):
        for route in self.routes:
            path, handler, methods = route
            app.add_route(path, handler, methods)
    
    def add_route(self, path, view_func, methods=None):
        self.routes.append((path, view_func, methods))
    
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

