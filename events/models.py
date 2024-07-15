from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel

from blog.models import Category, Organization, Person
from content_manager.abstract import SitesFacilesBasePage
from content_manager.models import Tag


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
        today = timezone.now().date()
        posts = (
            EventEntryPage.objects.descendant_of(self)
            .live()
            .filter(event_date_start__date__gte=today)
            .order_by("-event_date_start")
            .select_related("owner")
            .prefetch_related("tags", "event_categories", "date__year")
        )
        return posts

    def get_context(self, request, tag=None, category=None, author=None, source=None, year=None, *args, **kwargs):
        context = super(EventsIndexPage, self).get_context(request, *args, **kwargs)
        posts = self.posts
        # locale = Locale.objects.get(language_code=get_language())

        breadcrumb = None
        extra_title = ""

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

        if breadcrumb:
            context["breadcrumb"] = breadcrumb

        return context

    def get_authors(self) -> models.QuerySet:
        ids = self.posts.specific().values_list("authors", flat=True)
        return Person.objects.filter(id__in=ids).order_by("name")

    def get_categories(self) -> models.QuerySet:
        ids = self.posts.specific().values_list("event_categories", flat=True)
        return Category.objects.filter(id__in=ids).order_by("name")

    def get_sources(self) -> models.QuerySet:
        ids = self.posts.specific().values_list("authors__organization", flat=True)
        return Organization.objects.filter(id__in=ids).order_by("name")

    def get_tags(self) -> models.QuerySet:
        ids = self.posts.specific().values_list("tags", flat=True)
        return Tag.objects.filter(id__in=ids).order_by("name")


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
