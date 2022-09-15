from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import View

from oauthclient.client import OAuth2Client
from oauthclient.models import Provider, Token


class AuthCodeView(View):
    def get(self, *args, **kwargs):
        """
        Receives the OAuth2 authorization request

        :param args:
        :param kwargs:
        :return:
        """
        token_uuid = self.request.GET['state']
        token = Token.objects.get(uuid=token_uuid)
        provider = token.provider

        OAuth2Client(provider, token).set_token_from_auth_code(self.request.GET['code'])

        url = reverse('oauthclient:token', kwargs=dict(uuid=token.uuid))

        return redirect(url)


class AuthenticateView(View):
    def get(self, *args, **kwargs):
        token_uuid = kwargs['token_uuid']
        token = Token.objects.get(uuid=token_uuid)

        redirect_uri = self.request.build_absolute_uri(reverse('oauthclient:auth_code'))

        # extract the UUID field from the Token model
        provider_logic = OAuth2Client(token.provider, token=token)
        url = provider_logic.get_authentication_url(redirect_uri)

        return redirect(url)


class AuthorizeView(View):
    def get(self, *args, **kwargs):
        uuid = kwargs['uuid']
        provider = Provider.objects.get(uuid=uuid)

        try:
            token = provider.token_set.get()
        except Token.DoesNotExist:
            token = provider.token_set.create()

        # TODO: redirect to the AuthenticateView instead of copying this logic
        redirect_uri = self.request.build_absolute_uri(reverse('oauthclient:auth_code'))

        # extract the UUID field from the Token model
        provider_logic = OAuth2Client(provider, token=token)
        url = provider_logic.get_authentication_url(redirect_uri)

        return redirect(url)


class ProviderView(View):
    def get(self, *args, **kwargs):
        provider_uuid = kwargs['uuid']
        provider = Provider.objects.get(uuid=provider_uuid)

        ctx = {
            'provider': provider,
        }

        return render(self.request, 'oauthclient/provider_detail.html', ctx)


class TokenView(View):
    def get(self, *args, **kwargs):
        uuid = kwargs['uuid']
        token = Token.objects.get(uuid=uuid)

        ctx = {
            'token': token,
        }

        return render(self.request, 'oauthclient/token_detail.html', ctx)
