from rest_framework import serializers

from core.utils import TimeZone
from user_mgmt.models import UserMaster


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaster
        fields = '__all__'

    def create(self, validated_data):
        validated_data['updated_at'] = TimeZone.datetime()
        user = UserMaster.objects.create_user(**validated_data)
        return user

