from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from taggit.models import Tag as TaggitTag, TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
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

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("body", heading=_("body")),
    ]

    class Meta:
        verbose_name = _("Blog page")


@register_snippet
class Category(models.Model):
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
        return str(self.name)

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


class CategoryEntryPage(models.Model):
    category = models.ForeignKey(Category, related_name="+", verbose_name=_("Category"), on_delete=models.CASCADE)
    page = ParentalKey("BlogEntryPage", related_name="entry_categories")
    panels = [FieldPanel("category")]

    def __str__(self):
        return str(self.category)


class TagEntryPage(TaggedItemBase):
    content_object = ParentalKey("BlogEntryPage", related_name="entry_tags")


@register_snippet
class Tag(TaggitTag):
    objects = TagManager()

    class Meta:
        proxy = True