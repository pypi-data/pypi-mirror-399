# authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser

class ClerkAuthentication(BaseAuthentication):
    """
    DRF Authentication class.

    Note: If ClerkMiddleware is installed, request.user might already be set.
    However, DRF auth runs *after* middleware but *before* views.
    """

    def authenticate(self, request):
        # 1. If Middleware already did the work and found a valid user, trust it.
        # Check if request.user is populated and is not Anonymous
        if hasattr(request, 'user') and request.user.is_authenticated:
            return (request.user, None)

        # 2. If Middleware didn't run or returned Anonymous, we force a check here.
        # This allows this Auth class to work standalone without the Middleware.

        # Trigger the lazy evaluation if using middleware
        if hasattr(request, 'user') and not request.user.is_authenticated:
             # If middleware ran and resolved to AnonymousUser, we return None.
             # Returning None means "I don't know this user, try the next Auth class".
             # If permissions are IsAuthenticated, DRF will then raise 401.
             return None

        # 3. Standalone Fallback (if Middleware is NOT used)
        # We try to resolve the user manually using the logic from middleware
        from .middleware import get_user_from_token

        user = get_user_from_token(request)

        if user and user.is_authenticated:
            return (user, None)

        # If we found a token but it failed validation, strictly speaking standard DRF
        # conventions say: if token is present but invalid -> Raise AuthenticationFailed.
        # If no token -> Return None.

        auth_header = request.META.get('HTTP_AUTHORIZATION', b'')
        if auth_header:
            # Token was provided but get_user_from_token returned Anonymous
            raise exceptions.AuthenticationFailed('Invalid or expired Clerk token.')

        return None