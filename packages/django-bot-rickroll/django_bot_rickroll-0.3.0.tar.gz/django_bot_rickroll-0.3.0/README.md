# django-bot-rickroll

## Story

Once upon a time I noticed my server log was filled with 404 errors
for URL's like `/wp-admin` and so on.
I figured redirecting them to this [cool music video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
was one way I could get these errors out of my logs.

Also it means if my kids are snooping around they can get a laugh or two.

## Installation

```bash
uv add django-bot-rickroll
```

## Usage

Just add one line to `urlpatterns`:

```python
from django.urls import path, include

urlpatterns = [
    # Your app URLs first ...
    path("", include("bot_rickroll.urls")),
]
```

You should add this as the last line, so that in the unlikely event
one of the URL's in the blocklist is actually supposed to work,
then yours take precedence.

You can customize the target URL in your `settings.py`:

```python
RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## URL's covered

- `/wp-admin/`, `/wp-content/`, `/wp-includes/`, `/wp-json/`
- `/wordpress/`, `/wp/`
- `/administrator/`, `/joomla/`, `/drupal/`, `/magento/`, `/cms/`
- `/phpmyadmin/`, `/phpMyAdmin/`, `/pma/`, `/mysql/`, `/adminer/`
- `/cpanel/`, `/webmail/`, `/plesk/`
- `/file-manager/`, `/filemanager/`, `/laravel-file-manager/`, `/elfinder/`
- `/upload/`, `/uploads/`, `/files/`
- `/vendor/`, `/public/`, `/modules/`, `/node_modules/`
- `/lib/`, `/libraries/`, `/includes/`, `/inc/`
- `/.well-known/`, `/.git/`, `/.svn/`, `/.hg/`
- `/.env`, `/.htaccess`, `/.htpasswd`
- `/config/`, `/configuration/`, `/conf/`, `/settings/`
- `/backup/`, `/backups/`, `/bak/`
- `/old/`, `/temp/`, `/tmp/`
- `/cgi-bin/`, `/cgi/`, `/bin/`, `/scripts/`
- `/php/`
- `/db/`, `/database/`, `/sql/`
- Any URL ending in `.php`

## License

MIT
