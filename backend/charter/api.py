from ninja import NinjaAPI
from ninja.security import django_auth

from accounts.api import router as accounts_router
from datasets.api import router as datasets_router

api = NinjaAPI(
    title="Chart-er API",
    version="2",
    auth=django_auth,
    docs_url="/docs",
)

api.add_router("/auth", accounts_router)
api.add_router("/datasets", datasets_router)
