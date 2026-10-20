from django.core.management.commands import migrate
from django.db.migrations.operations import CreateModel
from wagtail.blocks import Block
from wagtail.fields import StreamField


class Command(migrate.Command):
    """
    Limit the memory used by Django's migrate command.

    Rendering the migration states builds the blocks of the StreamFields defined in the
    migrations, and these blocks are never released:
    - each StreamField of the migration operations caches its blocks (`stream_block`),
      and the operations are kept by the migration loader until the end of the process;
    - Wagtail keeps a reference to every block ever instantiated in `Block.definition_registry`.
    Each StreamField migration then adds dozens of megabytes to the memory used, until
    the process gets killed on small containers.

    Once each migration is done, the caches of the operation fields are dropped (they are
    rebuilt from `block_lookup` if needed), and the blocks created by the migrations are
    removed from the registry. The blocks of the actual models, created when the project
    is loaded, are kept.
    """

    def handle(self, *args, **options):
        self.initial_block_definitions = set(Block.definition_registry)
        self.done_migrations = []
        return super().handle(*args, **options)

    def migration_progress_callback(self, action, migration=None, fake=False):
        super().migration_progress_callback(action, migration, fake)

        if action in ("apply_success", "unapply_success"):
            self.done_migrations.append(migration)

            # The latest definition of each field is still used by the migration state, and
            # keeps its cache; the previous ones are replaced and can be cleared
            stream_fields = {}
            for done_migration in self.done_migrations:
                for operation in done_migration.operations:
                    if isinstance(operation, CreateModel):
                        model_name, fields = operation.name_lower, operation.fields
                    elif hasattr(operation, "field"):
                        model_name, fields = operation.model_name_lower, [(operation.name, operation.field)]
                    else:
                        continue
                    for field_name, field in fields:
                        if isinstance(field, StreamField):
                            key = (done_migration.app_label, model_name, field_name)
                            stream_fields.setdefault(key, []).append(field)

            for fields in stream_fields.values():
                for field in fields[:-1]:
                    field.__dict__.pop("stream_block", None)

            for definition_prefix in set(Block.definition_registry) - self.initial_block_definitions:
                del Block.definition_registry[definition_prefix]
