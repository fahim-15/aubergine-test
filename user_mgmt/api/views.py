from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from core.tasks import send_email_bg
from core.utils import generate_jwt_payload, jwt_encode_handler, TimeZone, create_account_verification_msg, \
    jwt_decode_handler
from user_mgmt.api.serializers import UserDetailSerializer
from user_mgmt.models import UserMaster


class UserDetailView(APIView):
    """

    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Get user details.")
    def get(self, request, user_id=None):
        try:
            if request.user.is_anonymous:
                return Response({'message': 'Not allowed.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
            if user_id is not None:
                user = UserMaster.objects.get(id=user_id, is_active=True)
                user_srlzr = UserDetailSerializer(user)
                return Response({'message': 'User Details.', 'code': 200,
                                 'object': user_srlzr.data},
                                status=status.HTTP_200_OK)
            users = UserMaster.objects.filter(is_active=True).order_by('first_name', 'last_name')
            user_srlzr = UserDetailSerializer(users, many=True)
            return Response({'message': 'List of users Details.', 'code': 200,
                             'object': user_srlzr.data},
                            status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'message': 'Something went wrong.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'mobile': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'address': openapi.Schema(type=openapi.TYPE_STRING),
            'state': openapi.Schema(type=openapi.TYPE_STRING),
            'country': openapi.Schema(type=openapi.TYPE_STRING),
            'pincode': openapi.Schema(type=openapi.TYPE_STRING)
        },
    ),
                         operation_description="Create User")
    def post(self, request):
        try:
            user_srlzr = UserDetailSerializer(data=request.data)
            if user_srlzr.is_valid():
                response = user_srlzr.save()
                payload = generate_jwt_payload(request, user=response.id, days=1)
                jwt_token = jwt_encode_handler(payload)
                msg = create_account_verification_msg(response, jwt_token)
                send_email_bg.delay(msg, 'Aubergine Test App Verify Account', [response.email])
                return Response({'message': 'User registered successfully. Please verified the account by clicking the '
                                            'verification link sent on registered email address.', 'code': 201},
                                status=status.HTTP_201_CREATED)
            return Response({'message': user_srlzr.errors, 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print(err)
            return Response({'message': 'Something went wrong.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['POST'], request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING)
        },
    ),
        operation_description="User Login")
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    try:
        username = request.data['username']
        password = request.data['password']
        user = UserMaster.objects.get(username=username)

        if not user.is_verified:
            return Response({'message': 'Account not verified. Please verified the account by clicking the verification'
                                        ' link sent on registered email address.', 'code': 400},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            payload = generate_jwt_payload(request, user=user.id)
            jwt_token = jwt_encode_handler(payload)
            user.last_login = TimeZone.datetime()
            user.save()
            return Response({'object': {'token': jwt_token}, 'message': 'Login successful.', 'code': 200},
                            status=status.HTTP_200_OK)

    except Exception as err:
        print(err)
        return Response({'message': 'Something went wrong.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def verify_account(request):
    try:
        token = request.GET.get('q')
        payload = jwt_decode_handler(token)
        UserMaster.objects.filter(id=payload['user']).update(is_verified=True)
        return Response({'message': 'Account verified successfully.', 'code': 200},
                        status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Something went wrong.', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
