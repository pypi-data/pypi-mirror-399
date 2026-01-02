from typing import Optional


class SecretProvider:
    """
    Abstract secrets provider.

    Implementations:
    - AWS Secrets Manager
    - Azure Key Vault
    - HashiCorp Vault
    """

    def get_secret(self, name: str) -> Optional[str]:
        raise NotImplementedError


class InMemorySecretProvider(SecretProvider):
    """
    Development-only secret provider.
    """

    def __init__(self, secrets: dict[str, str]):
        self._secrets = secrets

    def get_secret(self, name: str) -> Optional[str]:
        return self._secrets.get(name)
