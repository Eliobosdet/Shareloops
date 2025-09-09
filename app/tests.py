from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Loop, Tag, Genre
from .utils import process_tags_from_request


class UtilsFunctionTestCase(TestCase):
    """Test minimo per la funzione process_tags_from_request"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.existing_tag = Tag.objects.create(name='hip-hop')

    def test_process_tags_from_request_json_format(self):
        """Verifica che i tag vengano creati/recuperati da JSON"""
        factory = RequestFactory()
        request = factory.post('/', data={
            'tags': ['hip-hop', 'new-tag']
        })
        request.user = self.user

        print("🔍 Incoming POST data:", request.POST)

        post_data, processed_tag_ids = process_tags_from_request(request)

        self.assertEqual(len(processed_tag_ids), 2)
        self.assertTrue(Tag.objects.filter(name='new-tag').exists())
        self.assertTrue(all(tag_id.isdigit() for tag_id in post_data.getlist('tags')))


class HomePageViewTestCase(TestCase):
    """Test minimo per la home page"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', password='testpass123')
        self.genre = Genre.objects.create(name='Hip-Hop')
        self.tag = Tag.objects.create(name='hip-hop')

        self.audio = SimpleUploadedFile("audio.mp3", b"fake audio content", content_type="audio/mpeg")
        self.image = SimpleUploadedFile("cover.jpg", b"fake image content", content_type="image/jpeg")

        self.loop = Loop.objects.create(
            title="Test Loop",
            user=self.user,
            bpm=90,
            key="C",
            genre=self.genre,
            audio_file=self.audio,
            cover_image=self.image
        )
        self.loop.tags.add(self.tag)

    def test_home_page_loads_and_displays_content(self):
        """Verifica caricamento home page e contenuto"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Loop")
        self.assertContains(response, "90 BPM")
