from django.apps import AppConfig as DjangoAppConfig
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_clerk_sdk.signals import clerk_auth_success, clerk_auth_failed, clerk_cache_miss


# your_project/apps.py


# Imagine you have a datadog client
# from datadog import statsd

class DjangoClerkSDKConfig(DjangoAppConfig):
    name = 'django_clerk_sdk'
    label = _('Django Clerk SDK')

    def ready(self):
        @receiver(clerk_auth_success)
        def track_auth_success(sender, user, source, **kwargs):
            # statsd.increment('clerk.auth.success', tags=[f'source:{source}'])
            print(f"METRIC: Auth Success via {source} for {user.username}")

        @receiver(clerk_cache_miss)
        def track_cache_miss(sender, token_hash, **kwargs):
            # statsd.increment('clerk.auth.cache_miss')
            print("METRIC: Cache Miss")

        @receiver(clerk_auth_failed)
        def track_auth_fail(sender, reason, **kwargs):
            # statsd.increment('clerk.auth.failed', tags=[f'reason:{reason}'])
            print(f"METRIC: Auth Failed - {reason}")
