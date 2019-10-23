import os

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_LOGIN_BUILD_URL = ("https://accounts.google.com/.well-known/openid-configuration")
REDIRECT_URI = 'https://localhost:5000/login/callback'