from django.urls import include, path
from django.utils.translation import gettext as _
from wagtail import urls as wagtail_urls

from content_manager.views import SearchResultsView, SiteMapView, TagsListView, TagView

urlpatterns = [
    path(_("search/"), SearchResultsView.as_view(), name="cms_search"),
    path(_("sitemap/"), SiteMapView.as_view(), name="readable_sitemap"),
    path("tags/<str:tag>/", TagView.as_view(), name="global_tag"),
    path("tags/", TagsListView.as_view(), name="global_tags_list"),
    path("", include(wagtail_urls)),
]
