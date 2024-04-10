from django.shortcuts import render
from .forms import VideoForm

def home(request):
    app_name = 'Fun Music Videos' 
    return render(request, 'video_collection/home.html', {'app_name': app_name})


def add(request):
    new_video_form = VideoForm()
    return render(request, 'video_collection.html', {'new_video_form': new_video_form})