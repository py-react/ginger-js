import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request,FastAPI



def match_static_to_dynamic(static_path, dynamic_path_pattern):
    """
    Checks if the static_path matches the dynamic_path_pattern.

    Args:
        static_path (str): The static path to check.
        dynamic_path_pattern (str): The dynamic path pattern with placeholders (e.g., /api/test/{testId}).

    Returns:
        bool: True if the static path matches the dynamic path pattern, otherwise False.
    """
    # Convert dynamic path pattern to regex
    # Example: /api/test/{testId} => ^/api/test/(?P<testId>[^/]+)$
    pattern = dynamic_path_pattern
    pattern = re.sub(r'\{(\w+)\}', r'[^/]+', pattern)  # Replace {param} with a regex for non-slash characters
    pattern = '^' + pattern + '$'  # Anchor pattern to match the entire path

    # Match static path against the regex pattern
    return re.fullmatch(pattern, static_path) is not None

def Create_Layout_Middleware_Class(middleware_func,route):
    class Middleware(BaseHTTPMiddleware):
            def __init__(self, app: FastAPI):
                super().__init__(app)

            async def request_handler(self, request, call_next):
                response = await middleware_func(request,call_next)
                return response

            async def dispatch(self, request: Request, call_next):
                # Check if the request path needs authentication
                if match_static_to_dynamic(request.url.path,route) and not request.url.path.startswith("/api/"):
                    layoutData = await middleware_func(request)
                    if hasattr(request,"prop_data"):
                        request.state.prop_data[route] = layoutData
                    else:
                        request.state.prop_data = {}
                        request.state.prop_data[route] = layoutData
                    
                response = await call_next(request)
                return response
            
    return Middleware
