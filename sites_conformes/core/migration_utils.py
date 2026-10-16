"""Helpers shared by data migrations of several apps."""


def rename_revision_field(app_label: str, model_name: str, old_name: str, new_name: str):
    """
    RunPython callables (forward, backward) renaming a field in the stored revisions of a model,
    alongside a RenameField: modelcluster drops the unknown keys when it loads a revision,
    so the drafts would otherwise lose that field.
    """

    def rename(source: str, target: str):
        def run(apps, schema_editor):
            ContentType = apps.get_model("contenttypes", "ContentType")
            Revision = apps.get_model("wagtailcore", "Revision")
            content_type = ContentType.objects.filter(app_label=app_label, model=model_name.lower()).first()
            if content_type is None:
                return
            for revision in Revision.objects.filter(content_type=content_type, content__has_key=source):
                revision.content[target] = revision.content.pop(source)
                revision.save(update_fields=["content"])

        return run

    return rename(old_name, new_name), rename(new_name, old_name)


def keep_root_filter_categories(app_label: str, model_name: str):
    """
    RunPython callable: drops the subcategories chosen as filter groups on an index page model,
    on the pages and in their revisions, now that only root categories can be groups.
    Left in place, they would stay invisible in the admin and make the page fail to save.
    """

    def forward(apps, schema_editor):
        model = apps.get_model(app_label, model_name)
        Category = apps.get_model("sites_conformes_core", "Category")
        model.filter_categories.through.objects.filter(category__parent__isnull=False).delete()

        ContentType = apps.get_model("contenttypes", "ContentType")
        Revision = apps.get_model("wagtailcore", "Revision")
        content_type = ContentType.objects.filter(app_label=app_label, model=model_name.lower()).first()
        if content_type is None:
            return
        root_ids = set(Category.objects.filter(parent__isnull=True).values_list("pk", flat=True))
        for revision in Revision.objects.filter(content_type=content_type, content__has_key="filter_categories"):
            chosen = revision.content["filter_categories"] or []
            kept = [pk for pk in chosen if pk in root_ids]
            if kept != chosen:
                revision.content["filter_categories"] = kept
                revision.save(update_fields=["content"])

    return forward
