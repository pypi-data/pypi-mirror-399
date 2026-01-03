from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
import json

class OpenAPISchema:
    def __init__(self, title="API Documentation", version="1.0.0", description=""):
        self.title = title
        self.version = version
        self.description = description
        self.schema = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description
            },
            "paths": {}
        }
    
    def add_path(self, path, method, summary="", description="", request_body=None, responses=None, tags=None):
        if path not in self.schema["paths"]:
            self.schema["paths"][path] = {}
        
        path_item = {}
        
        if summary:
            path_item["summary"] = summary
        if description:
            path_item["description"] = description
        
        if request_body:
            path_item["requestBody"] = request_body
        
        if tags:
            path_item["tags"] = tags
        
        if responses:
            path_item["responses"] = responses
        else:
            path_item["responses"] = {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        
        self.schema["paths"][path][method.lower()] = path_item
    
    def get_schema(self):
        return self.schema
    
    def to_json(self):
        return json.dumps(self.schema, indent=2, ensure_ascii=False)

def get_swagger_ui_html(schema_url="/openapi.json"):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin: 0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: '{schema_url}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""
    return html

def get_redoc_html(schema_url="/openapi.json"):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url='{schema_url}'></redoc>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
    return html

class DocumentedRoute:
    def __init__(self, path, handler, methods, summary="", description="", 
                 request_body=None, responses=None, tags=None):
        self.path = path
        self.handler = handler
        self.methods = methods
        self.summary = summary
        self.description = description
        self.request_body = request_body
        self.responses = responses
        self.tags = tags or []

