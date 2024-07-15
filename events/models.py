from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel

from blog.models import Category
from content_manager.abstract import SitesFacilesBasePage


class EventsIndexPage(SitesFacilesBasePage):
    posts_per_page = models.PositiveSmallIntegerField(
        default=10,
        validators=[MaxValueValidator(100), MinValueValidator(1)],
        verbose_name=_("Posts per page"),
    )

    settings_panels = SitesFacilesBasePage.settings_panels + [
        FieldPanel("posts_per_page"),
    ]

    subpage_types = ["events.EventEntryPage"]

    class Meta:
        verbose_name = _("Event calendar index")

    @property
    def posts(self):
        # Get list of event pages that are descendants of this page
        posts = EventEntryPage.objects.descendant_of(self).live()
        posts = (
            posts.order_by("-date").select_related("owner").prefetch_related("tags", "event_categories", "date__year")
        )
        return posts


class EventEntryPage(SitesFacilesBasePage):
    tags = ClusterTaggableManager(through="TagEventEntryPage", blank=True)

    event_categories = ParentalManyToManyField(
        "blog.Category",
        through="CategoryEventEntryPage",
        blank=True,
        verbose_name=_("Categories"),
    )

    date = models.DateTimeField(verbose_name=_("Post date"), default=timezone.now)
    event_date_start = models.DateTimeField(verbose_name=_("Event start date"), default=timezone.now)
    event_date_end = models.DateTimeField(verbose_name=_("Event end date"), default=timezone.now)
    authors = ParentalManyToManyField(
        "blog.Person", blank=True, help_text=_("Author entries can be created in Snippets > Persons")
    )

    parent_page_types = ["events.EventsIndexPage"]
    subpage_types = []

    settings_panels = SitesFacilesBasePage.settings_panels + [
        FieldPanel("authors"),
        FieldPanel("date"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("event_date_start"),
                        FieldPanel("event_date_end"),
                    ],
                    classname="label-above",
                ),
            ],
            _("Event date"),
        ),
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
                FieldPanel("event_categories"),
                FieldPanel("tags"),
            ],
            heading=_("Tags and Categories"),
        ),
    ]

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Event page")


class TagEventEntryPage(TaggedItemBase):
    content_object = ParentalKey("EventEntryPage", related_name="event_entry_tags")


class CategoryEventEntryPage(models.Model):
    category = models.ForeignKey(Category, related_name="+", verbose_name=_("Category"), on_delete=models.CASCADE)
    page = ParentalKey("EventEntryPage", related_name="event_entry_categories")
    panels = [FieldPanel("category")]

    def __str__(self):
        return self.category
