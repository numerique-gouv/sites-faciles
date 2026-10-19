import gc
import weakref

from django.core.management.commands import migrate
from django.db.migrations.operations import CreateModel
from wagtail.blocks import Block


class Command(migrate.Command):
    """
    Keep the memory used by the migrate command low.

    Every StreamField migration builds the whole block tree of its fields, and Wagtail never
    releases it: the field caches it in its `stream_block` property, the field is kept by the
    migration operation for the whole run, and every block is also kept by the global
    `Block.definition_registry`. With many StreamField migrations to apply, the memory grows
    by tens of MB per migration, and a postdeploy on a small container is killed (OOM).
    """

    def handle(self, *args, **options):
        # The registry is only used to preview blocks in the admin, so holding the blocks
        # created by migrations weakly is enough
        registry = Block.definition_registry
        Block.definition_registry = weakref.WeakValueDictionary(registry)
        try:
            return super().handle(*args, **options)
        finally:
            registry.update(Block.definition_registry)
            Block.definition_registry = registry

    def migration_progress_callback(self, action, migration=None, fake=False):
        super().migration_progress_callback(action, migration, fake)
        if action in ("apply_success", "unapply_success"):
            release_stream_blocks(migration)


def release_stream_blocks(migration):
    for operation in migration.operations:
        fields = [field for _, field in operation.fields] if isinstance(operation, CreateModel) else []
        if getattr(operation, "field", None) is not None:
            fields.append(operation.field)

        for field in fields:
            field.__dict__.pop("stream_block", None)

    gc.collect()
