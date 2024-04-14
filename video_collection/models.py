from django.db import models
from urllib import parse
from django.core.exceptions import ValidationError

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # if not self.url.startswith('https://www.youtube.com/watch'):
        #     raise ValidationError(f'Not a Youtube URL {self.url}')
        # Extract video id from youtube url

        url_components = parse.urlparse(self.url)
        
        if url_components.scheme != 'https':
            raise ValidationError(f'Invalid Youtube URL {self.url}')

        if url_components.netloc != 'www.youtube.com':
            raise ValidationError(f'Invalid Youtube URL {self.url}')

        if url_components.path != '/watch':
            raise ValidationError(f'Invalid Youtube URL {self.url}')

        
        query_string = url_components.query # 'v=1234567'
        if not query_string:
            raise ValidationError(f'Invalid Youtube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) # dictionary
        v_parameters_list = parameters.get('v') # return None if key not found
        if not v_parameters_list:  # Check if None or empty List.
            raise ValidationError(f'Invalid Youtube URL, missing parameters {self.url}') 
        self.video_id = v_parameters_list[0] # string

        super().save(*args, **kwargs)  # run the rest of the save function

    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID:{self.video_id}, Notes: {self.notes[:200]}'
    