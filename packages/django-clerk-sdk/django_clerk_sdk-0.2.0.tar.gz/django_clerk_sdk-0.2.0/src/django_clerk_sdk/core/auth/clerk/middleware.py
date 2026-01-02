import hashlib
import logging
import httpx
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header

from .sdk import clerk_client
from .conf import conf
from django_clerk_sdk.core.signals import clerk_auth_success, clerk_auth_failed, clerk_cache_miss  # <--- Import signals

logger = logging.getLogger(__name__)


def get_cache_key(token: str) -> str:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return f"clerk:auth:{token_hash}"


def get_user_from_token(request):
    auth_header = get_authorization_header(request).split()
    if not auth_header or auth_header[0].lower() != b'bearer' or len(auth_header) != 2:
        return AnonymousUser()

    try:
        raw_token = auth_header[1].decode()
    except UnicodeError:
        # Emit failure signal
        clerk_auth_failed.send(sender=request.__class__, reason="unicode_error", token_hash=None)
        return AnonymousUser()

    cache_key = get_cache_key(raw_token)
    user_pk = cache.get(cache_key)

    # --- HIT ---
    if user_pk:
        try:
            user = clerk_client.User.objects.get(pk=user_pk)
            # Emit Success (Source: Cache)
            clerk_auth_success.send(sender=request.__class__, user=user, source="cache")
            return user
        except clerk_client.User.DoesNotExist:
            cache.delete(cache_key)

    # --- MISS ---
    # Emit Cache Miss
    clerk_cache_miss.send(sender=request.__class__, token_hash=cache_key)

    try:
        # ... (headers setup code) ...

        headers = {}
        for k, v in request.META.items():
            if k.startswith("HTTP_"):
                headers[k[5:].replace("_", "-")] = v
        headers["Authorization"] = request.META.get("HTTP_AUTHORIZATION", "")

        httpx_req = httpx.Request(
            method=request.method,
            url=request.build_absolute_uri(),
            headers=headers
        )

        user_id = clerk_client.authenticate_request(httpx_req)
        clerk_user_data = clerk_client.get_user_details(user_id)
        django_user = clerk_client.sync_django_user(clerk_user_data)

        cache.set(cache_key, django_user.pk, timeout=conf.CACHE_TIMEOUT)

        # Emit Success (Source: API)
        clerk_auth_success.send(sender=request.__class__, user=django_user, source="api")

        return django_user

    except Exception as e:
        logger.warning(f"Clerk Auth Failed: {e}")
        # Emit Failure
        clerk_auth_failed.send(sender=request.__class__, reason=str(e), token_hash=cache_key)
        return AnonymousUser()


class ClerkMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Lazy loading ensures we don't hit Cache/DB for static files
        # or public views unless request.user is actually accessed.
        request.user = SimpleLazyObject(lambda: get_user_from_token(request))