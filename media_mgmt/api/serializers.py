from rest_framework import serializers

from core.utils import TimeZone, generates_presigned_url
from media_mgmt.models import GalleryMaster


class GalleryMasterSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GalleryMaster
        fields = '__all__'

    def get_thumbnail_url(self, instance):
        return generates_presigned_url(instance.thumbnail_key)


