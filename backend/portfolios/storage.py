from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PortfolioStorage(S3Boto3Storage):
    """
    Custom S3 storage for portfolio CV files.
    
    Uses AWS S3 for production, falls back to local storage for development.
    """
    location = 'portfolios'
    file_overwrite = False
    default_acl = 'private'
    
    def __init__(self, *args, **kwargs):
        # Only use S3 if credentials are configured
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            super().__init__(*args, **kwargs)
        else:
            # Fall back to default storage for local development
            from django.core.files.storage import FileSystemStorage
            self.__class__ = FileSystemStorage
