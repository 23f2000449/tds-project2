from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from importlib import import_module
import os

# Standard FastAPI app name
app = FastAPI()

def create_endpoint_func(mod):
    async def endpoint_func(request: Request):
        params = dict(request.query_params)
        try:
            body = await request.json()
        except Exception:
            body = {}
        req_data = {
            "params": params,
            "body": body,
            "headers": dict(request.headers)
        }
        try:
            result = mod.handler(req_data)
            return JSONResponse(content=jsonable_encoder(result))
        except Exception as e:
            return JSONResponse(
                content={
                    "error": str(e),
                    "endpoint": str(mod.__name__)
                },
                status_code=500
            )
    return endpoint_func

def register_handlers(app):
    handlers_dir = os.path.join(os.path.dirname(__file__), "handlers")
    for filename in sorted(os.listdir(handlers_dir)):
        if filename.endswith(".py") and filename != "__init__.py":
            base = filename[:-3]
            endpoint = "/" if base == "root" else f"/{base}"
            mod = import_module(f"handlers.{base}")
            print(f"Registering endpoint: {endpoint}")
            app.add_api_route(endpoint, create_endpoint_func(mod), methods=["GET", "POST"])

register_handlers(app)
