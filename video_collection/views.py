from django.shortcuts import render
from .forms import VideoForm
from django.contrib import messages

def home(request):
    app_name = 'Fun Music Videos' 
    return render(request, 'video_collection/home.html', {'app_name': app_name})


def add(request):

    # Validation and security
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            new_video_form.save()
            messages.info(request, 'New video saved!')
            # TODO success message or redirect to video list
        else:
            messages.warning(request, 'Please check the data entered')
            return render(request, 'video_collection/add.html')
    
    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})