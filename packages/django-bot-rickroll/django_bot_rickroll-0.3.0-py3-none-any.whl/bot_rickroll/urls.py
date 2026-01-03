"""Include these patterns at the END of your urlpatterns to catch requests
that don't match your actual application routes.
"""

from django.urls import path, re_path

from .views import RickrollView


# Helper to generate path patterns for a directory prefix
def _rickroll_paths(prefix: str) -> list:
    """Generate path patterns for a directory and its subpaths."""
    view = RickrollView.as_view()
    return [
        path(f"{prefix}/", view),
        path(f"{prefix}/<path:path>", view),
    ]


# Directory prefixes to rickroll
_PREFIXES = [
    # WordPress
    "wp-admin",
    "wp-content",
    "wp-includes",
    "wp-json",
    "wordpress",
    "wp",
    # CMS and admin
    "administrator",
    "joomla",
    "drupal",
    "magento",
    "cms",
    # Database admin
    "phpmyadmin",
    "phpMyAdmin",
    "pma",
    "mysql",
    "myadmin",
    "adminer",
    # Hosting panels
    "cpanel",
    "webmail",
    "plesk",
    # File managers and uploads
    "file-manager",
    "filemanager",
    "laravel-file-manager",
    "elfinder",
    "upload",
    "uploads",
    "files",
    # Framework/library paths
    "vendor",
    "public",
    "modules",
    "node_modules",
    "lib",
    "libraries",
    "includes",
    "inc",
    # Sensitive paths
    ".well-known",
    ".git",
    ".svn",
    ".hg",
    "config",
    "configuration",
    "conf",
    "settings",
    # Backup paths
    "backup",
    "backups",
    "bak",
    "old",
    "temp",
    "tmp",
    # CGI and server
    "cgi-bin",
    "cgi",
    "bin",
    "scripts",
    "php",
    # Database paths
    "db",
    "database",
    "sql",
]

# Build urlpatterns from prefixes
urlpatterns = []
for prefix in _PREFIXES:
    urlpatterns.extend(_rickroll_paths(prefix))

# Add standalone file patterns
_view = RickrollView.as_view()
urlpatterns.extend(
    [
        path(".env", _view),
        path(".htaccess", _view),
        path(".htpasswd", _view),
        path("blog-verify", _view),
        # Catch-all for any .php file
        re_path(r"^.*\.php$", _view),
        # Catch-all for any wlwmanifest.xml file
        re_path(r"^.*wlwmanifest\.xml$", _view),
    ]
)
