from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import BooleanBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from content_manager.constants import (
    HEADING_CHOICES_2_5,
)


class RecentEntriesStructValue(blocks.StructValue):
    """
    Get and filter the recent entries for either a blog index or an events page index
    """

    def posts(self):
        index_page = self.get("index_page")
        is_blog = False

        if not index_page:
            is_blog = True
            index_page = self.get("blog")

        posts = index_page.posts

        category_filter = self.get("category_filter")
        if category_filter:
            if is_blog:
                posts = posts.filter(blog_categories=category_filter)
            else:
                posts = posts.filter(event_categories=category_filter)

        tag_filter = self.get("tag_filter")
        if tag_filter:
            posts = posts.filter(tags=tag_filter)

        author_filter = self.get("author_filter")
        if author_filter:
            posts = posts.filter(authors=author_filter)

        source_filter = self.get("source_filter")
        if source_filter:
            posts = posts.filter(authors__organization=source_filter)

        entries_count = self.get("entries_count")
        return posts[:entries_count]

    def current_filters(self) -> dict:
        filters = {}

        category_filter = self.get("category_filter")
        if category_filter:
            filters["category"] = category_filter.slug

        tag_filter = self.get("tag_filter")
        if tag_filter:
            filters["tag"] = tag_filter.slug

        author_filter = self.get("author_filter")
        if author_filter:
            filters["author"] = author_filter.id

        source_filter = self.get("source_filter")
        if source_filter:
            filters["source"] = source_filter.slug

        return filters

    def sub_heading_tag(self):
        """
        Used for the filters section titles
        """
        heading_tag = self.get("heading_tag")
        if heading_tag == "h2":
            return "h3"
        elif heading_tag == "h3":
            return "h4"
        elif heading_tag == "h4":
            return "h5"
        else:
            return "h6"


class HeadingTitleBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), required=False)
    heading_tag = blocks.ChoiceBlock(
        label=_("Heading level"),
        choices=HEADING_CHOICES_2_5,
        required=False,
        default="h2",
        help_text=_("Adapt to the page layout. Defaults to heading 2."),
    )


class FilterEntries(blocks.StructBlock):
    entries_count = blocks.IntegerBlock(
        label=_("Number of entries"), required=False, min_value=1, max_value=8, default=3
    )
    category_filter = SnippetChooserBlock("blog.Category", label=_("Filter by category"), required=False)
    tag_filter = SnippetChooserBlock("content_manager.Tag", label=_("Filter by tag"), required=False)
    author_filter = SnippetChooserBlock("blog.Person", label=_("Filter by author"), required=False)
    source_filter = SnippetChooserBlock(
        "blog.Organization",
        label=_("Filter by source"),
        help_text=_("The source is the organization of the post author"),
        required=False,
    )
    show_filters = BooleanBlock(label=_("Show filters"), default=False, required=False)


class BlogEntries(blocks.StructBlock):
    blog = blocks.PageChooserBlock(label=_("Blog"), page_type="blog.BlogIndexPage")


class BlogRecentEntriesBlock(FilterEntries, BlogEntries, HeadingTitleBlock):

    class Meta:
        icon = "placeholder"
        template = ("content_manager/blocks/blog_recent_entries.html",)
        value_class = RecentEntriesStructValue


class EventsEntries(blocks.StructBlock):
    index_page = blocks.PageChooserBlock(label=_("Event calendar"), page_type="events.EventsIndexPage")


class EventsRecentEntriesBlock(FilterEntries, EventsEntries, HeadingTitleBlock):

    class Meta:
        icon = "placeholder"
        template = ("content_manager/blocks/events_recent_entries.html",)
        value_class = RecentEntriesStructValue
