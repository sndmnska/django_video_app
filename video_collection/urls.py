from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Homepage
    path('add', views.add, name='add_video')
]


# XXX There were approximately 12 minutes left of video 2. 