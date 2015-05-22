from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'is_active',
            'email', 'username',
            'profile',
        )
