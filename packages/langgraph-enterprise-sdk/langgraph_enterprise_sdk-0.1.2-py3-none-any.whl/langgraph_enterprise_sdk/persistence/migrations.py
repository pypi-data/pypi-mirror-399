class Migration:
    """
    Represents a persistence migration.
    """

    def __init__(self, version: int, description: str):
        self.version = version
        self.description = description

    def apply(self) -> None:
        raise NotImplementedError


class MigrationRunner:
    """
    Applies persistence migrations in order.
    """

    def __init__(self):
        self._migrations: list[Migration] = []

    def register(self, migration: Migration) -> None:
        self._migrations.append(migration)
        self._migrations.sort(key=lambda m: m.version)

    def run(self) -> None:
        for migration in self._migrations:
            migration.apply()
