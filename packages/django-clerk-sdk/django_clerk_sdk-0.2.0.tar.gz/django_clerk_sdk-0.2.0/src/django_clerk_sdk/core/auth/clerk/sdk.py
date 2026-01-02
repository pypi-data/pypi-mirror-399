# sdk.py
import logging
import threading
from typing import Optional, Dict, Any

import httpx
from clerk_backend_api import Clerk, AuthenticateRequestOptions
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

from .conf import conf

logger = logging.getLogger(__name__)
User = get_user_model()

class ClerkClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        
        self.client = Clerk(bearer_auth=conf.SECRET_KEY)
        self._initialized = True

    def authenticate_request(self, request: httpx.Request) -> str:
        """
        Validates the request with Clerk and returns the User ID (sub).
        Raises Exception if validation fails.
        """
        options = AuthenticateRequestOptions(authorized_parties=conf.AUTHORIZED_PARTIES)
        
        # The Clerk SDK expects a specific request shape, we rely on the SDK to handle it
        outcome = self.client.authenticate_request(request, options)
        
        if not outcome.is_signed_in:
             raise Exception("Request not signed in")
             
        # Extract the user ID (sub) from the verified payload
        payload = outcome.payload or {}
        user_id = payload.get("sub")
        
        if not user_id:
            raise Exception("No 'sub' claim in token payload")
            
        return user_id

    def get_user_details(self, user_id: str):
        """
        Fetches raw user data from Clerk API.
        """
        return self.client.users.get(user_id=user_id)

    def sync_django_user(self, clerk_user_data: Any) -> Any:
        """
        Synchronizes a Clerk User object to a Django User model.
        """
        # 1. Determine Lookup Field
        clerk_id = getattr(clerk_user_data, "id")
        email_addresses = getattr(clerk_user_data, "email_addresses", [])
        primary_email_id = getattr(clerk_user_data, "primary_email_address_id", None)
        
        email = None
        for email_obj in email_addresses:
            if getattr(email_obj, "id") == primary_email_id:
                email = getattr(email_obj, "email_address")
                break
        
        # 2. Try to find user by Clerk ID first (Best Practice)
        user = None
        if hasattr(User, 'clerk_user_id'):
            user = User.objects.filter(clerk_user_id=clerk_id).first()

        # 3. Fallback to Email lookup if not found by ID
        if not user and email:
            user = User.objects.filter(email=email).first()

        # 4. Prepare Data for Update/Create
        defaults = {
            "first_name": getattr(clerk_user_data, "first_name", "") or "",
            "last_name": getattr(clerk_user_data, "last_name", "") or "",
            "is_active": True, # Ensure they can login
        }
        
        if hasattr(User, 'clerk_user_id'):
            defaults["clerk_user_id"] = clerk_id
            
        if hasattr(User, 'image'):
             defaults["image"] = getattr(clerk_user_data, "profile_image_url", None)

        if hasattr(User, 'last_active_at'):
             defaults["last_active_at"] = getattr(clerk_user_data, "last_active_at", None)

        # 5. Create or Update
        if user:
            # Update existing
            changed = False
            for key, value in defaults.items():
                if getattr(user, key) != value:
                    setattr(user, key, value)
                    changed = True
            if changed:
                user.save()
        else:
            # Create new
            if not email:
                 # If we are here, we have no user and no email to create one.
                 # Depending on strictness, we might raise or generate a fake email.
                 logger.error(f"Cannot create user for Clerk ID {clerk_id}: No email found.")
                 raise Exception("Cannot create user without email address")

            username_field = getattr(User, 'USERNAME_FIELD', 'username')
            # Handle username generation if it's not the email
            if username_field != 'email':
                defaults[username_field] = getattr(clerk_user_data, "username", None) or email.split('@')[0]
            
            defaults['email'] = email
            
            user = User.objects.create(**defaults)
            user.set_unusable_password()
            user.save()

        return user

# Global instance
clerk_client = ClerkClient()