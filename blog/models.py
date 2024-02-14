from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Count
from django.db.models.expressions import F
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag as TaggitTag, TaggedItemBase
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.models.i18n import Locale, TranslatableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from blog.managers import CategoryManager, TagManager
from content_manager.constants import STREAMFIELD_COMMON_FIELDS


class BlogIndexPage(Page):
    description = models.CharField(max_length=255, null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description", heading=_("Description")),
    ]

    subpage_types = ["blog.BlogEntryPage"]

    class Meta:
        verbose_name = _("Blog index")

    @property
    def posts(self):
        # Get list of blog pages that are descendants of this page
        posts = BlogEntryPage.objects.descendant_of(self).live()
        posts = (
            posts.order_by("-date").select_related("owner").prefetch_related("tags", "blog_categories", "date__year")
        )
        return posts

    def get_context(self, request, tag=None, category=None, author=None, year=None, *args, **kwargs):  # NOSONAR
        context = super(BlogIndexPage, self).get_context(request, *args, **kwargs)
        posts = self.posts
        locale = Locale.objects.get(language_code=get_language())

        if tag is None:
            tag = request.GET.get("tag")
        if tag:
            posts = posts.filter(tags__slug=tag)
        if category is None:  # Not coming from category_view in views.py
            if request.GET.get("category"):
                category = get_object_or_404(
                    Category,
                    slug=request.GET.get("category"),
                    locale=locale,
                )
        if category:
            if not request.GET.get("category"):
                category = get_object_or_404(Category, slug=category, locale=locale)
            posts = posts.filter(blog_categories__slug=category.slug)
        if author:
            if isinstance(author, str) and not author.isdigit():
                posts = posts.filter(author__username=author)
            else:
                posts = posts.filter(author_id=author)

        if year:
            posts = posts.filter(date__year=year)

        # Pagination
        page = request.GET.get("page")
        page_size = 10

        paginator = Paginator(posts, page_size)  # Show 10 posts per page
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context["posts"] = posts
        if category is not None:
            context["category"] = category.name
        context["tag"] = tag
        context["author"] = author
        context["year"] = year
        context["paginator"] = paginator

        return context

    def list_categories(self) -> list:
        posts = self.posts.specific()
        return (
            posts.values(
                cat_slug=F("blog_categories__slug"),
                cat_name=F("blog_categories__name"),
            )
            .annotate(cat_count=Count("cat_slug"))
            .filter(cat_count__gte=1)
            .order_by("-cat_count")
        )

    def list_tags(self, min_count: int = 1) -> list:
        posts = self.posts.specific()
        return (
            posts.values(tag_name=F("tags__name"), tag_slug=F("tags__slug"))
            .annotate(tag_count=Count("tag_slug"))
            .filter(tag_count__gte=min_count)
            .order_by("-tag_count")
        )


class BlogEntryPage(Page):
    body = StreamField(
        STREAMFIELD_COMMON_FIELDS,
        blank=True,
        use_json_field=True,
    )
    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Header image"),
    )
    tags = ClusterTaggableManager(through="TagEntryPage", blank=True)
    blog_categories = models.ManyToManyField(
        "Category",
        through="CategoryEntryPage",
        blank=True,
        verbose_name=_("Categories"),
    )
    date = models.DateTimeField(verbose_name=_("Post date"), default=timezone.now)

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("header_image"),
        FieldPanel("body", heading=_("body")),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("owner", heading=_("Author")),
        FieldPanel("date"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("go_live_at"),
                        FieldPanel("expire_at"),
                    ],
                    classname="label-above",
                ),
            ],
            _("Scheduled publishing"),
            classname="publishing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("blog_categories"),
                FieldPanel("tags"),
            ],
            heading=_("Tags and Categories"),
        ),
    ]

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Blog page")


@register_snippet
class Category(TranslatableMixin, index.Indexed, models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=_("Category name"))
    slug = models.SlugField(unique=True, max_length=80)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("Parent category"),
        on_delete=models.SET_NULL,
    )
    description = models.CharField(max_length=500, blank=True, verbose_name=_("Description"))

    objects = CategoryManager()

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent:
            parent = self.parent
            if self.parent == self:
                raise ValidationError(_("Parent category cannot be self."))
            if parent.parent and parent.parent == self:
                raise ValidationError(_("Cannot have circular Parents."))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)

    panels = [
        TitleFieldPanel("name"),
        FieldPanel("slug", widget=SlugInput),
        FieldPanel("description"),
        FieldPanel("parent"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = [
            ("translation_key", "locale"),
            ("name", "locale"),
            ("slug", "locale"),
        ]

    search_fields = [index.SearchField("name")]


class CategoryEntryPage(models.Model):
    category = models.ForeignKey(Category, related_name="+", verbose_name=_("Category"), on_delete=models.CASCADE)
    page = ParentalKey("BlogEntryPage", related_name="entry_categories")
    panels = [FieldPanel("category")]

    def __str__(self):
        return self.category


class TagEntryPage(TaggedItemBase):
    content_object = ParentalKey("BlogEntryPage", related_name="entry_tags")


@register_snippet
class Tag(TaggitTag):
    objects = TagManager()

    class Meta:
        proxy = True
