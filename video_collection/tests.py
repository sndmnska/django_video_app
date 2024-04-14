from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# Check if correct message is on the title page
class TestHomePageMessage(TestCase):
    
    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Fun Music Videos')

class TestAddVideos(TestCase):

    def test_add_video(self):
            valid_video = {
                'name': 'LIGHTS CAMERA ACTION! (stock images)',
                'url':  'https://www.youtube.com/watch?v=VkkS3kJAG7g',
                'notes': 'A silly little way to brighten up the day!'
            }

            url = reverse('add_video') # XXX Why do we reverse urls for testing again?
            # By default, django looks at immediate response. But in this case there's an additional request.
            # Follow = True, 
            response = self.client.post(url, data=valid_video, follow=True)  

            self.assertTemplateUsed('video_collection/video_list.html')
            
            # does the video list show the new video?
            self.assertContains(response, 'LIGHTS CAMERA ACTION! (stock images)')
            self.assertContains(response, 'https://www.youtube.com/watch?v=VkkS3kJAG7g')
            self.assertContains(response, 'A silly little way to brighten up the day!')

            video_count = Video.objects.count()
            self.assertEqual(1, video_count)

            video = Video.objects.first()

            self.assertEqual(video.name, 'LIGHTS CAMERA ACTION! (stock images)')
            self.assertEqual(video.url, 'https://www.youtube.com/watch?v=VkkS3kJAG7g')
            self.assertEqual(video.notes, 'A silly little way to brighten up the day!')
            self.assertEqual(video.video_id, 'VkkS3kJAG7g')


    def test_add_video_invalid_url_not_added(self):
        
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com'
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
        ]

        for invalid_video_url in invalid_video_urls:
            
            new_video = {
                'name':'example',
                'url': invalid_video_url,
                'notes':'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)

            self.assertTemplateUsed('video_collection/add.html') # Check the tempate used

            messages = response.context['messages']
            messages_texts = [message.message for message in messages] # Look at the message itself

            self.assertIn('Invalid YouTube URL', messages_texts) # I think check if *both* of these are sent as messages through django.
            self.assertIn('Please check the data entered', messages_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count) # Assert video count does not increase (stays at 0 )


class TestVideoList(TestCase):

    def test_all_videos_displayed_in_correct_order(self):
        
        # Make video objects in this test
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=def')
        v3 = Video.objects.create(name='len', notes='example', url='https://www.youtube.com/watch?v=meow')
        v4 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=rat')
        v5 = Video.objects.create(name='BBB', notes='example', url='https://www.youtube.com/watch?v=cat')

        expected_video_order = [ v2, v1, v5, v3, v4 ]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos']) # Convert from django QuerySet to a python list()
        # NOTE: context() is all the data combined with the template to display the page
        # In this case, response.context['videos'] is from the dict {'videos': videos, 'search_form': search_form} from views.py

        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No Videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_two_videos(self):
        Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
        Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=def')
        
        url = reverse('video_list')
        response = self.client.get(url)
        
        self.assertContains(response, '2 videos')


    def test_video_number_message_one_video(self):
        Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
        
        url = reverse('video_list')
        response = self.client.get(url)
        
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

class TestVideoSearch(TestCase):
    def test_video_search_matches(self):
        # Arrange
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
        v2 = Video.objects.create(name='AAABC', notes='example', url='https://www.youtube.com/watch?v=def')
        v3 = Video.objects.create(name='len', notes='example', url='https://www.youtube.com/watch?v=meow')
        v4 = Video.objects.create(name='ZXYabc', notes='example', url='https://www.youtube.com/watch?v=rat')
        v5 = Video.objects.create(name='BBB', notes='example', url='https://www.youtube.com/watch?v=cat')

        expected_video_order_abc_search_term = [v2, v1, v4]
        # Act
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])

        # Assert
        self.assertEqual(expected_video_order_abc_search_term, videos_in_template)
    

    def test_video_search_no_matches(self):
        # Arrange
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
        v2 = Video.objects.create(name='AAABC', notes='example', url='https://www.youtube.com/watch?v=def')
        v3 = Video.objects.create(name='len', notes='example', url='https://www.youtube.com/watch?v=meow')
        v4 = Video.objects.create(name='ZXYabc', notes='example', url='https://www.youtube.com/watch?v=rat')
        v5 = Video.objects.create(name='BBB', notes='example', url='https://www.youtube.com/watch?v=cat')

        expected_video_order = [] # empty list
        # Act
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])

        # Assert
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No Videos')

        
class TestVideoModel(TestCase):
    
    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=13245',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'http://www.youtube.com/watch?v=',
            'https://github.com'
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
        ]
        
        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_url, notes='example notes')

        # At the end, check that nothing has been added to db
        self.assertEqual(0, Video.objects.count())


    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=abc')
