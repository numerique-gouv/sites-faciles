from django.contrib.auth.models import User
from wagtail.models import Page
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase

from blog.models import BlogEntryPage, BlogIndexPage
from content_manager.models import ContentPage
from content_manager.utils import import_image
from events.models import EventEntryPage, EventsIndexPage

# Tests for blocks that have a value_class


class HorizontalCardBlockTestCase(WagtailPageTestCase):
    # Logic *should* be the same for a vertical card, but inside of a multiple columns block.
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()

        body = [
            (
                "card",
                {
                    "title": "Sample card",
                    "description": RichText('<p data-block-key="test">This is a sample card.</p>'),
                },
            )
        ]
        self.content_page = home.add_child(
            instance=ContentPage(title="Sample cards page", slug="content-page", owner=self.admin, body=body)
        )
        self.content_page.save()

    def test_basic_card_is_renderable(self):
        self.assertPageIsRenderable(self.content_page)

    def test_basic_card_has_structure_and_content(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.assertContains(
            response,
            "fr-card fr-card--horizontal",
        )
        self.assertInHTML("""<h3 class="fr-card__title">Sample card</h3>""", response.content.decode())
        self.assertInHTML(
            """<p class="fr-card__desc" data-block-key="test">This is a sample card.</p>""", response.content.decode()
        )

    def test_card_with_no_link_does_not_have_enlarge_class(self):
        url = self.content_page.url
        response = self.client.get(url)

        # The page header and footer have the class on the bloc-marque,
        # The card with no link should not, so count should be 2
        self.assertContains(response, "fr-enlarge-link", count=2)

    def test_card_with_main_link(self):
        body = [
            (
                "card",
                {"title": "Sample card", "description": "This is a sample card.", "url": "https://www.info.gouv.fr"},
            )
        ]
        self.content_page.body = body
        self.content_page.save()

        url = self.content_page.url
        response = self.client.get(url)

        # Count = 3 (page header and footer, card)
        self.assertContains(response, "fr-enlarge-link", count=3)

        self.assertInHTML("""<a href="https://www.info.gouv.fr">Sample card</a>""", response.content.decode())

    def test_card_with_cta_links(self):
        body = [
            (
                "card",
                {
                    "title": "Sample card",
                    "description": "This is a sample card.",
                    "url": "https://www.info.gouv.fr",
                    "call_to_action": [
                        {
                            "type": "links",
                            "value": [
                                {
                                    "type": "link",
                                    "value": {
                                        "page": None,
                                        "text": "Lien externe",
                                        "external_url": "https://numerique.gouv.fr",
                                    },
                                }
                            ],
                        }
                    ],
                },
            )
        ]
        self.content_page.body = body
        self.content_page.save()

        url = self.content_page.url
        response = self.client.get(url)

        # Count = 3 (page header and footer, but not the card as it has several links)
        self.assertContains(response, "fr-enlarge-link", count=2)

        self.assertInHTML("""<a href="https://www.info.gouv.fr">Sample card</a>""", response.content.decode())

        self.assertInHTML(
            """<ul class="fr-links-group">
                <li>
                    <a href="https://numerique.gouv.fr" target="_blank" rel="noopener external">Lien externe</a>
                </li>
            </ul>""",
            response.content.decode(),
        )

    def test_card_with_cta_buttons(self):
        body = [
            (
                "card",
                {
                    "title": "Sample card",
                    "description": "This is a sample card.",
                    "url": "https://www.info.gouv.fr",
                    "call_to_action": [
                        {
                            "type": "buttons",
                            "value": [
                                {
                                    "type": "button",
                                    "value": {
                                        "page": None,
                                        "text": "Label",
                                        "button_type": "fr-btn fr-btn--secondary",
                                        "external_url": "https://numerique.gouv.fr",
                                    },
                                },
                            ],
                        }
                    ],
                },
            )
        ]
        self.content_page.body = body
        self.content_page.save()

        url = self.content_page.url
        response = self.client.get(url)

        # Count = 3 (page header and footer, but not the card as it has several links)
        self.assertContains(response, "fr-enlarge-link", count=2)

        self.assertInHTML("""<a href="https://www.info.gouv.fr">Sample card</a>""", response.content.decode())

        self.assertInHTML(
            """<ul class="fr-btns-group fr-btns-group--inline-lg">
                <li>
                    <a class="fr-btn fr-btn--secondary"
                    href="https://numerique.gouv.fr"
                    target="_blank"
                    rel="noopener external">Label</a>
                </li>
            </ul>""",
            response.content.decode(),
        )

    def test_card_with_basic_top_tag(self):
        body = [
            (
                "card",
                {
                    "title": "Sample card",
                    "description": "This is a sample card.",
                    "url": "https://www.info.gouv.fr",
                    "top_detail_badges_tags": [
                        {
                            "type": "tags",
                            "value": [
                                {
                                    "type": "tag",
                                    "value": {
                                        "link": {"page": None, "external_url": ""},
                                        "color": "purple-glycine",
                                        "label": "Tag 1",
                                        "is_small": False,
                                        "icon_class": "fr-icon-community-fill",
                                    },
                                },
                            ],
                        }
                    ],
                },
            )
        ]
        self.content_page.body = body
        self.content_page.save()

        url = self.content_page.url
        response = self.client.get(url)

        # Count = 3 (page header and footer, card)
        self.assertContains(response, "fr-enlarge-link", count=3)

        self.assertInHTML("""<a href="https://www.info.gouv.fr">Sample card</a>""", response.content.decode())

        self.assertInHTML(
            """<ul class="fr-tags-group">
                <li>
                    <p class="fr-tag fr-tag--purple-glycine fr-icon-community-fill fr-tag--icon-left">Tag 1</p>
                </li>
            </ul>""",
            response.content.decode(),
        )

    def test_card_with_linked_top_tag(self):
        body = [
            (
                "card",
                {
                    "title": "Sample card",
                    "description": "This is a sample card.",
                    "url": "https://www.info.gouv.fr",
                    "top_detail_badges_tags": [
                        {
                            "type": "tags",
                            "value": [
                                {
                                    "type": "tag",
                                    "value": {
                                        "link": {"page": None, "external_url": "https://numerique.gouv.fr"},
                                        "color": "purple-glycine",
                                        "label": "Tag 1",
                                        "is_small": False,
                                        "icon_class": "fr-icon-community-fill",
                                    },
                                },
                            ],
                        }
                    ],
                },
            )
        ]
        self.content_page.body = body
        self.content_page.save()

        url = self.content_page.url
        response = self.client.get(url)

        # Count = 3 (page header and footer, but not the card as it has several links)
        self.assertContains(response, "fr-enlarge-link", count=2)

        self.assertInHTML("""<a href="https://www.info.gouv.fr">Sample card</a>""", response.content.decode())

        self.assertInHTML(
            """<ul class="fr-tags-group">
                <li>
                    <a href="https://numerique.gouv.fr"
                    class="fr-tag fr-tag--purple-glycine fr-icon-community-fill fr-tag--icon-left">Tag 1</a>
                </li>
            </ul>""",
            response.content.decode(),
        )


class TileBlockTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()

        body = [
            (
                "tile",
                {
                    "title": "Sample tile",
                    "description": RichText('<p data-block-key="test">This is a sample tile.</p>'),
                },
            )
        ]
        self.content_page = home.add_child(
            instance=ContentPage(title="Sample tiles page", slug="content-page", owner=self.admin, body=body)
        )
        self.content_page.save()

    def test_basic_tile_is_renderable(self):
        self.assertPageIsRenderable(self.content_page)

    def test_basic_tile_has_no_header_div(self):
        url = self.content_page.url

        response = self.client.get(url)

        self.assertNotContains(response, "fr-tile__header")

    def test_tile_with_image_has_div(self):
        image_file = "static/artwork/technical-error.svg"
        image = import_image(image_file, "Sample image")

        body = [
            (
                "tile",
                {
                    "title": "Sample tile",
                    "description": RichText('<p data-block-key="test">This is a sample tile.</p>'),
                    "image": image,
                },
            )
        ]

        self.content_page.body = body
        self.content_page.save()

        url = self.content_page.url

        response = self.client.get(url)

        self.assertContains(response, "fr-tile__header")


class BlogRecentEntriesBlockTestCase(WagtailPageTestCase):
    def setUp(self):
        home_page = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()

        lorem_raw = "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"
        lorem_body = []
        lorem_body.append(("paragraph", RichText(lorem_raw)))

        blog_index = home_page.add_child(
            instance=BlogIndexPage(title="Actualités", body=lorem_body, slug="actualités", show_in_menus=True)
        )

        _blog_entry = blog_index.add_child(instance=BlogEntryPage(title="Article", body=lorem_body, slug="article"))

        body = [
            (
                "blog_recent_entries",
                {"title": "Actus", "heading_tag": "h2", "blog": blog_index, "entries_count": 4},
            )
        ]
        self.content_page = home_page.add_child(
            instance=ContentPage(title="Sample page", slug="content-page", owner=self.admin, body=body)
        )
        self.content_page.save()

    def test_blog_recent_entries_is_renderable(self):
        self.assertPageIsRenderable(self.content_page)


class EventsRecentEntriesBlockTestCase(WagtailPageTestCase):
    def setUp(self):
        home_page = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()

        lorem_raw = "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"
        lorem_body = []
        lorem_body.append(("paragraph", RichText(lorem_raw)))

        events_index = home_page.add_child(
            instance=EventsIndexPage(title="Agenda", body=lorem_body, slug="agenda", show_in_menus=True)
        )

        _event_entry = events_index.add_child(
            instance=EventEntryPage(title="Formation", body=lorem_body, slug="formation")
        )

        body = [
            (
                "events_recent_entries",
                {"title": "Actus", "heading_tag": "h2", "index_page": events_index, "entries_count": 4},
            )
        ]
        self.content_page = home_page.add_child(
            instance=ContentPage(title="Sample page", slug="content-page", owner=self.admin, body=body)
        )
        self.content_page.save()

    def test_events_recent_entries_is_renderable(self):
        self.assertPageIsRenderable(self.content_page)
