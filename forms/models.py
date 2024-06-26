from django.db import models
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from dsfr.utils import dsfr_input_class_attr
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.fields import RichTextField


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
        ("date", _("Date")),
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
        if request.method == "POST":
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)

            if form.is_valid():
                form_submission = self.process_form_submission(form)
                return self.render_landing_page(request, form_submission, *args, **kwargs)
        else:
            form = self.get_form(page=self, user=request.user)

        for visible in form.visible_fields():
            dsfr_input_class_attr(visible)

        context = self.get_context(request)
        context["form"] = form
        return TemplateResponse(request, self.get_template(request), context)
