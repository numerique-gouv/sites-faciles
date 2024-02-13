from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag as TaggitTag, TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.fields import StreamField
from wagtail.models import Page
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


class BlogEntryPage(Page):
    body = StreamField(
        STREAMFIELD_COMMON_FIELDS,
        blank=True,
        use_json_field=True,
    )

    tags = ClusterTaggableManager(through="TagEntryPage", blank=True)
    blog_categories = models.ManyToManyField(
        "Category",
        through="CategoryEntryPage",
        blank=True,
        verbose_name=_("Categories"),
    )

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("body", heading=_("body")),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("tags"),
                FieldPanel("blog_categories"),
            ],
            heading=_("Tags and Categories"),
        ),
    ]

    class Meta:
        verbose_name = _("Blog page")


@register_snippet
class Category(index.Indexed, models.Model):
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
