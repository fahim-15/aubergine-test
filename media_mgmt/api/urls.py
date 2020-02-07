from django.urls import path
from .views import *

urlpatterns = [
    path('', GalleryMasterView.as_view()),
]