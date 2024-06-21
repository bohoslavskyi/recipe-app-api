from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            },
        }

    def create(self, validated_data: dict) -> User:
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={
            'input_type': 'password',
        },
        trim_whitespace=False,
    )

    def validate(self, attrs: dict) -> dict:
        email: str = attrs.get('email')
        password: str = attrs.get('password')
        user: User = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                detail=_('Unable to authenticate with provided credentials.'),
                code='authentication',
            )
        
        attrs['user'] = user

        return attrs