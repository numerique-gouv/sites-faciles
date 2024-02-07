from django.db import models
from django.forms import widgets
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from content_manager.blocks import (
    AccordionsBlock,
    AlertBlock,
    CalloutBlock,
    HeroBlock,
    ImageAndTextBlock,
    ImageBlock,
    MultiColumnsWithTitleBlock,
    QuoteBlock,
    SeparatorBlock,
    StepperBlock,
    TitleBlock,
    VideoBlock,
)


class ContentPage(Page):
    body = StreamField(
        [
            ("hero", HeroBlock(label="Section promotionnelle")),
            ("title", TitleBlock(label="Titre de page")),
            ("paragraph", blocks.RichTextBlock(label="Texte avec mise en forme")),
            (
                "paragraphlarge",
                blocks.RichTextBlock(label="Texte avec mise en forme (large)"),
            ),
            ("image", ImageBlock()),
            (
                "imageandtext",
                ImageAndTextBlock(label="Bloc image à gauche et texte à droite"),
            ),
            ("alert", AlertBlock(label="Message d'alerte")),
            ("callout", CalloutBlock(label="Texte mise en avant")),
            ("quote", QuoteBlock(label="Citation")),
            ("video", VideoBlock(label="Vidéo")),
            ("multicolumns", MultiColumnsWithTitleBlock(label="Multi-colonnes")),
            ("accordions", AccordionsBlock(label="Accordéons")),
            ("stepper", StepperBlock(label="Étapes")),
            ("separator", SeparatorBlock(label="Séparateur")),
        ],
        blank=True,
        use_json_field=True,
    )

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel("body", heading="Contenu"),
    ]

    # Inherit search_fields from Page and add body to index
    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "Page de contenu"
        verbose_name_plural = "Pages de contenu"


class MonospaceField(models.TextField):
    """
    A TextField which renders as a large HTML textarea with monospace font.
    """

    def formfield(self, **kwargs):
        kwargs["widget"] = widgets.Textarea(
            attrs={
                "rows": 12,
                "class": "monospace",
                "spellcheck": "false",
            }
        )
        return super().formfield(**kwargs)


@register_setting(icon="code")
class AnalyticsSettings(BaseSiteSetting):
    class Meta:
        verbose_name = "Scripts de suivi"

    head_scripts = MonospaceField(
        blank=True,
        null=True,
        verbose_name="Scripts de suivi <head>",
        help_text="Ajoutez des scripts de suivi entre les balises <head>.",
    )

    body_scripts = MonospaceField(
        blank=True,
        null=True,
        verbose_name="Scripts de suivi <body>",
        help_text="Ajoutez des scripts de suivi vers la fermeture de la balise <body>.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("head_scripts"),
                FieldPanel("body_scripts"),
            ],
            heading="Scripts de suivi",
        ),
    ]


@register_setting(icon="cog")
class CmsDsfrConfig(BaseSiteSetting):
    class Meta:
        verbose_name = "Configuration du site"

    header_brand = models.CharField(
        "Institution (en-tête)",
        max_length=200,
        default="Intitulé officiel",
        help_text="""Intitulé du bloc-marques tel que défini sur la page
        https://www.gouvernement.fr/charte/charte-graphique-les-fondamentaux/le-bloc-marque""",
        blank=True,
    )
    header_brand_html = models.CharField(
        "Institution avec césure (en-tête)",
        max_length=200,
        default="Intitulé<br />officiel",
        blank=True,
        help_text="""Intitulé du bloc-marques avec des balises <br />
        pour affichage sur plusieurs lignes""",
    )
    footer_brand = models.CharField(
        "Institution (pied)",
        max_length=200,
        default="Intitulé officiel",
        blank=True,
    )

    footer_brand_html = models.CharField(
        "Institution avec césure (pied)",
        max_length=200,
        default="Intitulé<br />officiel",
        blank=True,
    )

    site_title = models.CharField(
        "Titre du site",
        max_length=200,
        default="Titre du site",
        blank=True,
    )
    site_tagline = models.CharField(
        "Sous-titre du site",
        max_length=200,
        default="Sous-titre du site",
        blank=True,
    )
    footer_description = models.TextField(
        "Description",
        default="",
        blank=True,
        help_text="Balises HTML autorisés",
    )

    search_bar = models.BooleanField("Barre de recherche dans l’en-tête", default=False)
    theme_modale_button = models.BooleanField("Choix du thème clair/sombre", default=False)
    mourning = models.BooleanField("Mise en berne", default=False)

    panels = [
        FieldPanel("header_brand"),
        FieldPanel("header_brand_html"),
        FieldPanel("footer_brand"),
        FieldPanel("footer_brand_html"),
        FieldPanel("site_title"),
        FieldPanel("site_tagline"),
        FieldPanel("footer_description"),
        FieldPanel("search_bar"),
        FieldPanel("mourning"),
        FieldPanel("theme_modale_button"),
    ]


class FormField(AbstractFormField):
    FORM_FIELD_CHOICES = (
        ("singleline", _("Single line text")),
        ("multiline", _("Multi-line text")),
        ("email", _("Email")),
        ("number", _("Number")),
        ("url", _("URL")),
        ("checkbox", _("Checkbox")),
        ("cmsfr_checkboxes", _("Checkboxes")),
        ("dropdown", _("Drop down")),
        ("cmsfr_radio", _("Radio buttons")),
        ("cmsfr_date", _("Date")),
        ("cmsfr_datetime", _("Date/time")),
        ("hidden", _("Hidden field")),
    )

    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("intro", heading="Introduction"),
        InlinePanel("form_fields", label="Champs de formulaire"),
        FieldPanel("thank_you_text", heading="Texte de remerciement"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Courriel",
            help_text="Facultatif",
        ),
    ]

    class Meta:
        verbose_name = "Page de formulaire"
        verbose_name_plural = "Pages de formulaire"

    def serve(self, request, *args, **kwargs):
        # These input widgets don't need the fr-input class
        if request.method == "POST":
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)

            if form.is_valid():
                form_submission = self.process_form_submission(form)
                return self.render_landing_page(request, form_submission, *args, **kwargs)
        else:
            form = self.get_form(page=self, user=request.user)

        WIDGETS_NO_FR_INPUT = [
            widgets.CheckboxInput,
            widgets.FileInput,
            widgets.ClearableFileInput,
        ]

        for visible in form.visible_fields():
            """
            Depending on the widget, we have to add some classes:
            - on the outer group
            - on the form field itsef

            If a class is already set, we don't force the DSFR-specific classes.
            """
            if "class" not in visible.field.widget.attrs:
                if type(visible.field.widget) in [
                    widgets.Select,
                    widgets.SelectMultiple,
                ]:
                    visible.field.widget.attrs["class"] = "fr-select"
                    visible.field.widget.group_class = "fr-select-group"
                elif isinstance(visible.field.widget, widgets.DateInput):
                    visible.field.widget.attrs["class"] = "fr-input"
                    visible.field.widget.attrs["type"] = "date"
                elif isinstance(visible.field.widget, widgets.RadioSelect):
                    visible.field.widget.attrs["dsfr"] = "dsfr"
                    visible.field.widget.group_class = "fr-radio-group"
                elif isinstance(visible.field.widget, widgets.CheckboxSelectMultiple):
                    visible.field.widget.attrs["dsfr"] = "dsfr"
                elif type(visible.field.widget) not in WIDGETS_NO_FR_INPUT:
                    visible.field.widget.attrs["class"] = "fr-input"

        context = self.get_context(request)
        context["form"] = form
        return TemplateResponse(request, self.get_template(request), context)
