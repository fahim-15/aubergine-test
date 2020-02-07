from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import resize_image, generate_image_path, TimeZone, put_s3_object
from media_mgmt.api.serializers import GalleryMasterSerializer
from media_mgmt.models import GalleryMaster


class GalleryMasterView(APIView):

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image_urls': openapi.Schema(type=openapi.TYPE_ARRAY,
                                       items=openapi.Schema(type=openapi.TYPE_STRING))
        },
    ),
        operation_description="Add images.")
    def post(self, request):
        try:
            image_urls = request.data['image_urls']
            final_data = []
            for image in image_urls:
                compressed_img, image_format = resize_image(image)
                key = generate_image_path(request.user.email, image_format)
                put_s3_object(compressed_img, key)
                final_data.append({'original_url': image,
                                   'thumbnail_url': key,
                                   'user': request.user.id,
                                   'created_at': TimeZone.datetime(),
                                   'updated_at': TimeZone.datetime()})

            media_srlzr = GalleryMasterSerializer(data=final_data, many=True)
            if media_srlzr.is_valid():
                media_srlzr.save()
                return Response({'list': media_srlzr.data, 'message': 'Saved successfully.', 'code': 201},
                                status=status.HTTP_201_CREATED)
            print(media_srlzr.errors)
            return Response({'message': media_srlzr.errors, 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print(err)
            return Response({'message': 'Something went wrong.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description='Get Images.')
    def get(self, request, image_id=None):
        try:
            if image_id is None:
                images = GalleryMaster.objects.filter(user=request.user)
                image_srlzr = GalleryMasterSerializer(images, many=True)
                return Response({'list': image_srlzr.data, 'message': 'List of all image details.', 'code': 200},
                                status=status.HTTP_200_OK)
            image = GalleryMaster.objects.get(id=image_id)
            image_srlzr = GalleryMasterSerializer(image)
            return Response({'data': image_srlzr.data, 'message': 'Get single image detail.', 'code': 200},
                            status=status.HTTP_200_OK)
        except Exception as err:
            print(err)
            return Response({'message': 'Something went wrong.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)


