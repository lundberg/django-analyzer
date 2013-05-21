from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'django_test_project.views.analyze', name='analyze'),
)
