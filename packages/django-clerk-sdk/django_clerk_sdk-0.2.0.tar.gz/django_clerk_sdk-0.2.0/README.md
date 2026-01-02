# Django Clerk SDK

A robust, production-ready Django SDK for integrating [Clerk](https://clerk.com/) authentication into your Django and Django Rest Framework (DRF) applications.

This SDK handles JWT validation, automatic user synchronization between Clerk and Django, efficient caching to minimize API latency, and provides built-in signals for observability.

## Features

* **Seamless Authentication**: Middleware and DRF Authentication classes to validate Clerk Bearer tokens.
* **Automatic User Synchronization**: Automatically creates or updates Django users based on Clerk user data (syncs email, username, name, profile image, and activity status).
* **High Performance Caching**: Uses Django's cache framework to store validated tokens, minimizing round-trips to the Clerk API.
* **Flexible User Model**: Compatible with custom User models. Includes a ready-to-use `ClerkUser` model optimized for Clerk data.
* **Observability First**: Emits Django Signals (`success`, `failure`, `cache_miss`) for easy integration with monitoring tools like Datadog, Sentry, or Prometheus.

## Installation

1.  **Add to Installed Apps**

    Add the SDK and the users app (if you plan to use the provided User model) to your `INSTALLED_APPS` in `settings.py`:

    ```python
    INSTALLED_APPS = [
        # ... other apps
        'django_clerk_sdk',
        'django_clerk_sdk.users',  # Optional: If using the included ClerkUser model
    ]
    ```

2.  **Configure Middleware**

    Add the `ClerkMiddleware` to your `MIDDLEWARE` list. It should be placed after `SessionMiddleware` and before `CommonMiddleware`:

    ```python
    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        # ...
        'django_clerk_sdk.core.auth.clerk.middleware.ClerkMiddleware',
        # ...
    ]
    ```

3.  **Configure DRF Authentication**

    Set `ClerkAuthentication` as the default authentication class for Django Rest Framework:

    ```python
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'django_clerk_sdk.core.auth.clerk.authentication.ClerkAuthentication',
            # 'rest_framework.authentication.SessionAuthentication', # Optional fallback
        ),
    }
    ```

## Configuration

Add the following settings to your `settings.py`:

```python
# Required: Your Clerk Secret Key
CLERK_SECRET_KEY = "sk_test_..." 

# Required: List of authorized parties (your frontend URLs)
CLERK_AUTH_PARTIES = ["http://localhost:3000", "[https://your-app.com](https://your-app.com)"]

# Optional: Clerk API URL (Defaults to [https://api.clerk.com/v1](https://api.clerk.com/v1))
CLERK_API_URL = "[https://api.clerk.com/v1](https://api.clerk.com/v1)"

# Optional: Cache timeout in seconds (Defaults to 3600s / 1 hour)
REDIS_CACHE_TIMEOUT = 3600
```

## User Model Setup
The SDK works best with a User model that stores Clerk-specific fields. You can use the included ClerkUser model or integrate the fields into your own.

### Option A: Use the included ClerkUser
In `settings.py`:

```python
AUTH_USER_MODEL = "users.ClerkUser"
```

### Option B: Use your own Custom User Model
The SDK dynamically checks for the presence of fields before syncing. Ensure your custom model has the following fields to take full advantage of synchronization:

 - `clerk_user_id` (CharField, unique)

 - `email` (EmailField)

 - `username` (CharField)

 - `first_name` (CharField)

 - `last_name` (CharField)

 - `image` (URLField)

 - `last_active_at` (DateTimeField)

## Usage

1. **Authentication Flow**
    Once configured, the SDK automatically handles authentication:
    
    Middleware: Intercepts the request, checks for a Bearer token.
    
    Cache Check: Checks if the token is already validated and cached.
    
    Validation: If not cached, calls the Clerk API to validate the token.
    
    Sync: Fetches the latest user details from Clerk and updates the Django User record.
    
    Context: Sets request.user to the Django User instance.

2. **Protecting Views**
   Use standard DRF permissions. The authentication class ensures request.user is populated.

   ```Python
   
   from rest_framework.permissions import IsAuthenticated
   from rest_framework.views import APIView
   from rest_framework.response import Response
   
   class ProtectedView(APIView):
      permission_classes = [IsAuthenticated]
   
      def get(self, request):
          return Response({
              "message": f"Hello, {request.user.username}!",
              "clerk_id": request.user.clerk_user_id
          })
   ```
3. **Using the SDK Client directly**
   You can access the clerk_client singleton to interact with the SDK programmatically:

   ```Python
   from django_clerk_sdk.core.auth.clerk.sdk import clerk_client
   
   # Authenticate a request object manually
   user_id = clerk_client.authenticate_request(request)
   
   # Get raw user details from Clerk
   raw_user = clerk_client.get_user_details(user_id)
   
   # Manually sync a user
   user = clerk_client.sync_django_user(raw_user)
   ```

## Observability & Signals
The SDK emits Django signals to help you track authentication metrics. You can hook into these signals to log to Datadog, Sentry, or your console.

Available Signals:

`clerk_auth_success`: Sent on successful login (Args: `user`, `source="cache"|"api"`).

`clerk_auth_failed`: Sent on auth failure (Args: `reason`, `token_hash`).

`clerk_cache_miss`: Sent when a token is not found in cache.

Example Receiver:

```python
# apps.py
from django.apps import AppConfig
from django.dispatch import receiver
from django_clerk_sdk.core.signals import clerk_auth_success, clerk_auth_failed

class MyAppConfig(AppConfig):
    name = 'my_app'

    def ready(self):
        @receiver(clerk_auth_success)
        def log_success(sender, user, source, **kwargs):
            print(f"User {user.username} logged in via {source}")

        @receiver(clerk_auth_failed)
        def log_failure(sender, reason, **kwargs):
            print(f"Auth failed: {reason}")
```