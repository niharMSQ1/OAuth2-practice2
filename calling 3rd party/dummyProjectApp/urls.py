from django.urls import path
from .views import dummyApi

urlpatterns = [
    path('dummyApi/',dummyApi),
]
