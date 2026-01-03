from django.views.generic import RedirectView

from .settings import get_rickroll_url


class RickrollView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return get_rickroll_url()
