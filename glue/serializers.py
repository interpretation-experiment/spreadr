from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'url', 'id',
            'username',
            'profile', 'profile_url',
        )
