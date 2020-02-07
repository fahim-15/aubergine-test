import datetime
import requests
import io
import boto3
import jwt

from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from botocore.client import Config

from core.constants import JWT_DEFAULTS

from PIL import Image, ExifTags

from user_mgmt.models import UserMaster


class TimeZone:
    @staticmethod
    def datetime():
        return timezone.now()

    @staticmethod
    def time():
        return timezone.datetime.time(timezone.now())

    @staticmethod
    def date():
        return timezone.datetime.date(timezone.now())

    @staticmethod
    def timestamp():
        return timezone.now().timestamp()


def get_user_agent(request):
    return 'FAHIM'


def generate_jwt_payload(request, user=None, days=14):
    payload = {
        'user': user,
        'user_agent': get_user_agent(request),
        'iss': JWT_DEFAULTS['JWT_ISSUER'],
        'iat': TimeZone.datetime(),
        'exp': TimeZone.datetime() + datetime.timedelta(days=days)
    }
    return payload


def jwt_get_user_from_payload(payload):
    return payload.get('user')


def jwt_encode_handler(payload):
    key = settings.SECRET_KEY
    return jwt.encode(
        payload,
        key,
        JWT_DEFAULTS['JWT_ALGORITHM']
    ).decode('utf-8')


def jwt_decode_handler(token):
    options = {
        'verify_exp': JWT_DEFAULTS['JWT_VERIFY_EXPIRATION'],
    }
    secret_key = JWT_DEFAULTS['JWT_SECRET_KEY']
    return jwt.decode(
        token,
        secret_key,
        options=options,
        leeway=JWT_DEFAULTS['JWT_LEEWAY'],
        audience=JWT_DEFAULTS['JWT_AUDIENCE'],
        issuer=JWT_DEFAULTS['JWT_ISSUER'],
        algorithms=[JWT_DEFAULTS['JWT_ALGORITHM']]
    )


def generate_jwt_token(request, user_id):
    payload = generate_jwt_payload(request, user=user_id)
    jwt_token = jwt_encode_handler(payload)
    return jwt_token


def init_aws_session(service, region=None):
    if service == 's3':
        return boto3.client(service,
                            aws_access_key_id=settings.AWS_ACCESS_KEY,
                            aws_secret_access_key=settings.AWS_SECRET_KEY,
                            config=Config(signature_version='s3v4')
                            )
    return boto3.client(service,
                        aws_access_key_id=settings.AWS_ACCESS_KEY,
                        aws_secret_access_key=settings.AWS_SECRET_KEY,
                        config=Config(signature_version='s3v4'),
                        region_name=region
                        )


def create_account_verification_msg(user,  token):
    return f'Hi {user.first_name}\n\tPlease click on link to verify Aubergine Test App account,\n' \
           f'{settings.BASE_URL}/verify/?q={token}'


def send_email(message, subject, recipient=[]):
    send_mail(subject, message, settings.SENDER_EMAIL_ID, recipient, fail_silently=False)


def resize_image(public_url):
    img_byte_arr = io.BytesIO()

    response = requests.get(public_url)
    if response.content != b'':
        picture = Image.open(io.BytesIO(response.content))

        width = picture.size[0]
        height = picture.size[1]
        if width / height == 4 / 3:
            if width > 1280 and height > 960:
                width = 1280
                height = 960
        elif width / height == 3 / 4:
            if width > 960 and height > 1280:
                width = 960
                height = 1280
        elif width / height == 16 / 9:
            if width > 1280 and height > 720:
                width = 1280
                height = 720
        elif width / height == 9 / 16:
            if width > 720 and height > 1280:
                width = 720
                height = 1280
        elif height >= 3000 or width >= 3000:
            height //= 2
            width //= 2

        if picture.format == 'PNG':
            image_format = 'WEBP'
        else:
            image_format = picture.format
        picture = picture.resize((width, height), Image.ANTIALIAS)
        picture.save(img_byte_arr, image_format, optimize=True, progressive=True, quality=75)
        return img_byte_arr.getvalue(), image_format


def put_s3_object(body, key):
    client = init_aws_session('s3')
    response = client.put_object(
        ACL='public-read',
        Body=body,
        Bucket=settings.BUCKET_NAME,
        Key=key
    )


def generate_image_path(user_id, image_format):
    user = get_user_by_id(user_id)
    return f"{user.email.split('@')[0]}/{str(TimeZone.timestamp()).split('.')[0]}.{image_format.lower()}"


def generates_presigned_url(key):
    if key is '' or key is None:
        return ''
    s3 = init_aws_session('s3')
    url = s3.generate_presigned_url('get_object', Params={'Bucket': settings.BUCKET_NAME, 'Key': key}, ExpiresIn=10000)
    return url


def get_user_by_id(user_id):
    try:
        return UserMaster.objects.get(id=user_id)
    except:
        return None

