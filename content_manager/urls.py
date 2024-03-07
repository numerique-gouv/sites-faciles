from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from content_manager.views import SearchResultsView, TagsListView, TagView


urlpatterns = [
    path("cms-admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("recherche/", SearchResultsView.as_view(), name="cms_search"),
    path("", include("blog.urls", namespace="blog")),
    path("tags/<str:tag>/", TagView.as_view(), name="global_tag"),
    path("tags/", TagsListView.as_view(), name="global_tags_list"),
    path("", include(wagtail_urls)),
]
