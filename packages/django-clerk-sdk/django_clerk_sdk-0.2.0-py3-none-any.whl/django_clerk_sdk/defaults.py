from decouple import config

AUTH_USER_MODEL = "users.ClerkUser"

CLERK_SECRET_KEY = config('CLERK_SECRET_KEY', cast=str)
CLERK_AUTH_PARTIES = config('CLERK_AUTH_PARTIES', cast=list) # ["http://localhost:3000", ...] # Your frontend origins
CLERK_API_URL = config("CLERK_API_URL", cast=str) # "https://api.clerk.com/v1"
