from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from . models import Event

class StaticViewSitemap(Sitemap):
  def items(self):
    return ['home', 'about', 'create', 'recommendations', 'contact'] + list(Event.objects.all())

  def location(self, item):
    if isinstance(item, str):
          return reverse(item)
    elif isinstance(item, Event):
          return reverse('event', kwargs={'pk': item.pk})
    else:
          return None  



