from django.conf import settings

DEFAULT_RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def get_rickroll_url() -> str:
    """Get the rickroll URL from Django settings or use default."""
    return getattr(settings, "RICKROLL_URL", DEFAULT_RICKROLL_URL)
