from typing import Optional

import boto3


class AWSConnector:
    """
    AWS cloud connector.

    Used by:
    - S3 tools
    - Secrets
    - Cloud-native agents

    No business logic here.
    """

    def __init__(self, region: Optional[str] = None):
        self._region = region

    def s3(self):
        return boto3.client("s3", region_name=self._region)

    def secrets_manager(self):
        return boto3.client("secretsmanager", region_name=self._region)

    def sts(self):
        return boto3.client("sts", region_name=self._region)

    def health_check(self) -> bool:
        try:
            self.sts().get_caller_identity()
            return True
        except Exception:
            return False
