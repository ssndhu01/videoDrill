from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import *



class CommonModelsTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(username="testuser", password="testpassword")
        account = Accounts.objects.create(user=user, nickname="testaccount", is_authenticated=True,
                                           min_duration=5, max_file_size=10, max_duration=60)
        format1 = VideoFomats.objects.create(format="mp4")
        format2 = VideoFomats.objects.create(format="avi", active=False)
        format3 = VideoFomats.objects.create(format="mkv")
        account.allowed_formats.add(format1, format2)
        account.save()
        
    def testBooksPagination(self):
        self.assertEqual(Accounts.objects.count(), 1)
        self.assertEqual(VideoFomats.objects.count(), 3)
        account = Accounts.objects.get(nickname="testaccount")
        self.assertEqual(account.allowed_formats.count(), 2)

