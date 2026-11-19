from django.conf import settings
from django.db import connection
from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from accounts.api import me_router
from accounts.api import router as accounts_router
from charts.api import revisions_router
from charts.api import router as charts_router
from datasets.api import router as datasets_router

api = NinjaAPI(
    title="Chart-er API",
    version="2",
    auth=django_auth,
    docs_url="/docs",
)

api.add_router("/auth", accounts_router)
api.add_router("/me", me_router)
api.add_router("/datasets", datasets_router)
api.add_router("/charts", charts_router)
api.add_router("/revisions", revisions_router)


class Health(Schema):
    status: str
    version: str


@api.get("/health", auth=None, response={200: Health, 503: Health}, tags=["health"])
def health(request: HttpRequest):
    """Whether this server can answer, and which build it runs. `version` is
    the git commit the image was built from. Open to anyone: it is what a
    deploy or a monitor asks before trusting the rest."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return 503, {"status": "database unavailable", "version": settings.APP_VERSION}
    return 200, {"status": "ok", "version": settings.APP_VERSION}
