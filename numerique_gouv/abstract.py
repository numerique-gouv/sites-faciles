from wagtail.fields import StreamField

from content_manager.abstract import SitesFacilesBasePage
from content_manager.blocks import STREAMFIELD_COMMON_BLOCKS
from numerique_gouv.blocks import STREAMFIELD_NUMERIQUE_BLOCKS


class NumeriqueBasePage(SitesFacilesBasePage):
    body = StreamField(
        STREAMFIELD_COMMON_BLOCKS + STREAMFIELD_NUMERIQUE_BLOCKS,
        blank=True,
        use_json_field=True,
    )
