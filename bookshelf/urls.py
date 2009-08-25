from django.conf.urls.defaults import *

urlpatterns = patterns('bookshelf.views',
    (r'^$', 'books'),
)
