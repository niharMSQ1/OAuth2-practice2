from .views import dummyApi
from django.urls import path

urlpatterns = [
    path('dummyApi/', dummyApi),
]
