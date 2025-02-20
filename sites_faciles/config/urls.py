from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic.base import RedirectView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from sites_faciles.config.api import api_router

urlpatterns = [
    path(settings.WAGTAILADMIN_PATH, include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/v2/", api_router.urls),
    path("favicon.ico", RedirectView.as_view(url="/static/dsfr/dist/favicon/favicon.ico", permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("", include("sites_faciles_content_manager.urls")),
    prefix_default_language=False,
)

# Only add this on a dev machine, outside of tests
if not settings.TESTING and settings.DEBUG and "localhost" in settings.HOST_URL:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
