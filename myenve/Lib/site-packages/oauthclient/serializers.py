from rest_framework import serializers

from oauthclient.models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    """
    Serializes the Provider model

    This serializer does not include client_secret.
    """
    class Meta:
        model = Provider
        fields = (
            'uuid', 'name', 'client_id', 'auth_url', 'token_url', 'revoke_url',
        )


class SecretProviderSerializer(ProviderSerializer):
    """
    Serializes the Provider model including the client_secret
    """
    class Meta:
        model = Provider
        fields = ProviderSerializer.Meta.fields + ('client_secret',)
