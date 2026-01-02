# signals.py
import django.dispatch

# Sent when a user is successfully authenticated
# Provides args: user (User instance), source ("cache" or "api")
clerk_auth_success = django.dispatch.Signal()

# Sent when authentication fails
# Provides args: reason (str), token_hash (str)
clerk_auth_failed = django.dispatch.Signal()

# Sent when a cache miss occurs (helpful for tracking cache efficiency)
clerk_cache_miss = django.dispatch.Signal()