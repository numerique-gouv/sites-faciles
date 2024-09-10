from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import BooleanField, Count, QuerySet
from django.db.models.expressions import F
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from rest_framework import serializers
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable
from wagtail.models.i18n import Locale, TranslatableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from blog.blocks import COLOPHON_BLOCKS
from blog.managers import CategoryManager
from content_manager.abstract import SitesFacilesBasePage
from content_manager.constants import LIMITED_RICHTEXTFIELD_FEATURES
from content_manager.models import Tag

User = get_user_model()


@register_snippet
class Organization(Orderable):
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(max_length=80)

    panels = [
        TitleFieldPanel("name"),
        FieldPanel("slug", widget=SlugInput),
    ]

    api_fields = [
        APIField("name"),
        APIField("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Organization")


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug")


@register_snippet
class Person(Orderable):
    name = models.CharField(_("Name"), max_length=255)
    role = models.CharField(_("Role"), max_length=255)
    organization = models.ForeignKey("Organization", null=True, on_delete=models.SET_NULL)
    contact_info = models.CharField(_("Contact info"), max_length=500, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("organization"),
        FieldPanel("contact_info"),
        FieldPanel("image"),
    ]

    api_fields = [
        APIField("name"),
        APIField("role"),
        APIField("organization", serializer=OrganizationSerializer()),
        APIField("contact_info"),
        APIField("image"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Person")


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name", "role", "organization", "contact_info", "image")
        depth = 1


@register_snippet
class Category(TranslatableMixin, index.Indexed, Orderable):
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
    description = RichTextField(
        max_length=500,
        features=LIMITED_RICHTEXTFIELD_FEATURES,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Displayed on the top of the category page"),
    )
    colophon = StreamField(
        COLOPHON_BLOCKS,
        blank=True,
        use_json_field=True,
        help_text=_("Text displayed at the end of every page in the category"),
    )
    objects = CategoryManager()

    panels = [
        TitleFieldPanel("name"),
        FieldPanel("slug", widget=SlugInput),
        FieldPanel("description"),
        FieldPanel("colophon"),
        FieldPanel("parent"),
    ]

    api_fields = [
        APIField("name"),
        APIField("slug"),
        APIField("description"),
        APIField("colophon"),
        APIField("parent"),
    ]

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "colophon", "parent")
        depth = 1


class CategoryEntryPage(models.Model):
    category = models.ForeignKey(Category, related_name="+", verbose_name=_("Category"), on_delete=models.CASCADE)
    page = ParentalKey("BlogEntryPage", related_name="entry_categories")
    panels = [FieldPanel("category")]

    def __str__(self):
        return self.category


class TagEntryPage(TaggedItemBase):
    content_object = ParentalKey("BlogEntryPage", related_name="entry_tags")


class BlogIndexPage(SitesFacilesBasePage):
    posts_per_page = models.PositiveSmallIntegerField(
        default=10,
        validators=[MaxValueValidator(100), MinValueValidator(1)],
        verbose_name=_("Posts per page"),
    )

    # Filters
    filter_by_category = models.BooleanField(_("Filter by category"), default=True)
    filter_by_tag = models.BooleanField(_("Filter by tag"), default=True)
    filter_by_author = models.BooleanField(_("Filter by author"), default=False)
    filter_by_source = models.BooleanField(
        _("Filter by source"), help_text=_("The source is the organization of the post author"), default=False
    )

    settings_panels = SitesFacilesBasePage.settings_panels + [
        FieldPanel("posts_per_page"),
        MultiFieldPanel(
            [
                FieldPanel("filter_by_category"),
                FieldPanel("filter_by_tag"),
                FieldPanel("filter_by_author"),
                FieldPanel("filter_by_source"),
            ],
            heading=_("Show filters"),
        ),
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

    def get_context(self, request, tag=None, category=None, author=None, source=None, year=None, *args, **kwargs):
        context = super(BlogIndexPage, self).get_context(request, *args, **kwargs)
        posts = self.posts
        locale = Locale.objects.get(language_code=get_language())

        extra_breadcrumbs = None
        extra_title = ""

        if tag is None:
            tag = request.GET.get("tag")
        if tag:
            tag = get_object_or_404(Tag, slug=tag)
            posts = posts.filter(tags=tag)
            extra_breadcrumbs = {
                "links": [
                    {"url": self.get_url(), "title": self.title},
                    {
                        "url": reverse("blog:tags_list", kwargs={"blog_slug": self.slug}),
                        "title": _("Tags"),
                    },
                ],
                "current": tag,
            }
            extra_title = _("Posts tagged with %(tag)s") % {"tag": tag}

        if category is None:
            category = request.GET.get("category")
        if category:
            category = get_object_or_404(Category, slug=category, locale=locale)
            posts = posts.filter(blog_categories=category)

            extra_breadcrumbs = {
                "links": [
                    {"url": self.get_url(), "title": self.title},
                    {
                        "url": reverse("blog:categories_list", kwargs={"blog_slug": self.slug}),
                        "title": _("Categories"),
                    },
                ],
                "current": category.name,
            }
            extra_title = _("Posts in category %(category)s") % {"category": category.name}

        if source is None:
            source = request.GET.get("source")
        if source:
            source = get_object_or_404(Organization, slug=source)
            posts = posts.filter(authors__organization=source)
            extra_breadcrumbs = {
                "links": [
                    {"url": self.get_url(), "title": self.title},
                ],
                "current": _("Posts written by") + f" {source.name}",
            }
            extra_title = _("Posts written by") + f" {source.name}"

        if author is None:
            author = request.GET.get("author")
        if author:
            author = get_object_or_404(Person, id=author)

            extra_breadcrumbs = {
                "links": [
                    {"url": self.get_url(), "title": self.title},
                ],
                "current": _("Posts written by") + f" {author.name}",
            }
            posts = posts.filter(authors=author)
            extra_title = _("Posts written by") + f" {author.name}"

        if year:
            posts = posts.filter(date__year=year)
            extra_title = _("Posts published in %(year)s") % {"year": year}

        # Pagination
        page = request.GET.get("page")
        page_size = self.posts_per_page

        paginator = Paginator(posts, page_size)  # Show <page_size> posts per page
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context["posts"] = posts
        context["current_category"] = category
        context["current_tag"] = tag
        context["current_source"] = source
        context["current_author"] = author
        context["year"] = year
        context["paginator"] = paginator
        context["extra_title"] = extra_title

        # Filters
        context["categories"] = self.get_categories()
        context["authors"] = self.get_authors()
        context["sources"] = self.get_sources()
        context["tags"] = self.get_tags()

        if extra_breadcrumbs:
            context["extra_breadcrumbs"] = extra_breadcrumbs

        return context

    def get_authors(self) -> QuerySet:
        ids = self.posts.specific().values_list("authors", flat=True)
        return Person.objects.filter(id__in=ids).order_by("name")

    def get_categories(self) -> QuerySet:
        ids = self.posts.specific().values_list("blog_categories", flat=True)
        return Category.objects.filter(id__in=ids).order_by("name")

    def get_sources(self) -> QuerySet:
        ids = self.posts.specific().values_list("authors__organization", flat=True)
        return Organization.objects.filter(id__in=ids).order_by("name")

    def get_tags(self) -> QuerySet:
        ids = self.posts.specific().values_list("tags", flat=True)
        return Tag.objects.filter(id__in=ids).order_by("name")

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

    def show_filters(self) -> bool | BooleanField:
        return self.filter_by_category or self.filter_by_tag or self.filter_by_author or self.filter_by_source


class BlogEntryPage(SitesFacilesBasePage):
    tags = ClusterTaggableManager(through="TagEntryPage", blank=True)
    blog_categories = ParentalManyToManyField(
        "Category",
        through="CategoryEntryPage",
        blank=True,
        verbose_name=_("Categories"),
    )
    date = models.DateTimeField(verbose_name=_("Post date"), default=timezone.now)
    authors = ParentalManyToManyField(
        "blog.Person", blank=True, help_text=_("Author entries can be created in Snippets > Persons")
    )

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    settings_panels = SitesFacilesBasePage.settings_panels + [
        FieldPanel("authors"),
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

    api_fields = SitesFacilesBasePage.api_fields + [
        APIField("tags"),
        APIField("blog_categories", serializer=CategorySerializer(many=True)),
        APIField("authors", serializer=PersonSerializer(many=True)),
        APIField("go_live_at"),
        APIField("expire_at"),
    ]

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Blog page")
