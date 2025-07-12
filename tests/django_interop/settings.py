SECRET_KEY = "Insecure"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "tests.django_interop",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
