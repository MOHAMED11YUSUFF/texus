import os
from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount
from backend.fastapis.main import app as fastapi_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_asgi_app = get_asgi_application()

application = Starlette(routes=[
    Mount("/api", app=fastapi_app),     # FastAPI under /api
    Mount("/", app=django_asgi_app),    # Django handles rest
])