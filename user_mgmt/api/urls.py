from django.urls import path
from .views import *

urlpatterns = [
    path('', UserDetailView.as_view()),
    path('<int:user_id>/', UserDetailView.as_view()),
]