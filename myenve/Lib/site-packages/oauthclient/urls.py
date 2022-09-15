from __future__ import absolute_import

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',

    url(r'authenticate/(?P<token_uuid>[0-9a-fA-F]+)$', views.AuthenticateView.as_view(), name='authenticate'),
    url(r'auth_code$', views.AuthCodeView.as_view(), name='auth_code'),
    url(r'providers/(?P<uuid>[0-9a-fA-F]+)$', views.ProviderView.as_view(), name='provider'),
    url(r'providers/(?P<uuid>[0-9a-fA-F]+)/authorize$', views.AuthorizeView.as_view(), name='authorize'),
    url(r'tokens/(?P<uuid>[0-9a-fA-F]+)$', views.TokenView.as_view(), name='token'),
)
