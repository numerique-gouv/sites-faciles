from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import TemplateView
from unidecode import unidecode
from wagtail.models.i18n import Locale

from blog.models import BlogEntryPage, BlogIndexPage, Category


def get_localized_index(slug):
    locale = Locale.objects.get(language_code=get_language())
    return get_object_or_404(BlogIndexPage, locale=locale, slug=slug)


def tag_view(request, blog_slug: str, tag: str):
    index = get_localized_index(blog_slug)
    return index.serve(request, tag=tag)


def category_view(request, blog_slug: str, category: str):
    index = get_localized_index(blog_slug)
    return index.serve(request, category=category)


def author_view(request, blog_slug: str, author_id: str):
    index = get_localized_index(blog_slug)
    return index.serve(request, author=author_id)


def year_view(request, blog_slug: str, year: str):
    index = get_localized_index(blog_slug)
    return index.serve(request, year=year)


class LatestEntriesFeed(Feed):
    """
    If a URL ends with "rss" try to find a matching BlogIndexPage
    and return its items.
    """

    def get_object(self, request, *args, **kwargs):
        blog_slug = kwargs.pop("blog_slug")
        return get_object_or_404(BlogIndexPage, slug=blog_slug)

    def title(self, blog):
        if blog.seo_title:  # pragma: no cover
            return blog.seo_title
        return blog.title

    def link(self, blog):
        return blog.full_url

    def description(self, blog):
        return blog.search_description

    def items(self, blog):
        return blog.get_descendants().order_by("-first_published_at")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.body

    def item_link(self, item):
        return item.full_url

    def item_pubdate(self, blog):
        return blog.first_published_at


class LatestEntriesFeedAtom(LatestEntriesFeed):
    feed_type = Atom1Feed


class LatestCategoryFeed(Feed):
    description = "A Blog"

    def title(self, category):
        return "Blog: " + category.name

    def link(self, category):
        return "/blog/category/" + category.slug

    def get_object(self, request, *args, **kwargs):
        category = kwargs.pop("category")
        return get_object_or_404(Category, slug=category)

    def items(self, obj):
        return BlogEntryPage.objects.filter(blog_categories=obj).order_by("-date")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body


class CategoriesListView(TemplateView):
    template_name = "blog/categories_list_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = []
        blog_slug = kwargs.get("blog_slug")
        blog_index = get_localized_index(blog_slug)
        if blog_index:
            categories = blog_index.list_categories()

        breadcrumb = {
            "links": [
                {"url": blog_index.get_url(), "title": blog_index.title},
            ],
            "current": _("Categories"),
        }

        context["categories"] = categories
        context["page"] = blog_index
        context["breadcrumb"] = breadcrumb
        return context


class TagsListView(TemplateView):
    template_name = "blog/tags_list_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tags = []
        blog_slug = kwargs.get("blog_slug")
        blog_index = get_localized_index(blog_slug)
        if blog_index:
            tags = blog_index.list_tags()

        tags_by_first_letter = {}
        for tag in tags:
            first_letter = unidecode(tag["tag_slug"][0].upper())
            if first_letter not in tags_by_first_letter:
                tags_by_first_letter[first_letter] = []
            tags_by_first_letter[first_letter].append(tag)

        breadcrumb = {
            "links": [
                {"url": blog_index.get_url(), "title": blog_index.title},
            ],
            "current": _("Tags"),
        }

        context["sorted_tags"] = tags_by_first_letter
        context["page"] = blog_index
        context["breadcrumb"] = breadcrumb
        return context
