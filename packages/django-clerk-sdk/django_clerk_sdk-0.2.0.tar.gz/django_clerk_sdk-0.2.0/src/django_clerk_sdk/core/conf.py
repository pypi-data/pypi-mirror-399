from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class ClerkSettings:
    @property
    def SECRET_KEY(self):
        key = getattr(settings, "CLERK_SECRET_KEY", None)
        if not key:
            raise ImproperlyConfigured("CLERK_SECRET_KEY is not set.")
        return key

    @property
    def AUTHORIZED_PARTIES(self):
        return getattr(settings, "CLERK_AUTH_PARTIES", [])

    @property
    def CACHE_TIMEOUT(self):
        # Default to 5 minutes (300s) if not set.
        # This is a good balance between performance and data freshness.
        return getattr(settings, 'CLERK_CACHE_TIMEOUT', 300)

conf = ClerkSettings()