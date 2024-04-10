from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        # List the fields from the Video model to show in the form
        model = Video
        fields = ['name', 'url', 'notes']
