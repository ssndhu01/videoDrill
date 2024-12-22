import json
import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage as Storage
from common.models import Accounts, VideoFomats, AccountTokens
from django.conf import settings
from .models import *

class VideoUploadTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(username="testuser", password="testpassword")    
        account = Accounts.objects.create(user=user, nickname="testaccount", is_authenticated=True,
                                           min_duration=5, max_file_size=4, max_duration=10)
        format1 = VideoFomats.objects.create(format="mp4")
        format2 = VideoFomats.objects.create(format="avi")
        format3 = VideoFomats.objects.create(format="mkv")  
        account.allowed_formats.add(format1, format2)   
        account.save()
        tokens = AccountTokens.objects.create(account=account, token_name="testtoken")
        tokens.save()
        self.account = account

        account1 = Accounts.objects.create(user=user, nickname="testaccount", is_authenticated=True,
                                           min_duration=5, max_file_size=50, max_duration=300)        

        account1.allowed_formats.add(format1, format3, format2)   
        account1.save()
        tokens1 = AccountTokens.objects.create(account=account1, token_name="testtoken1")
        self.account1 = account1


    def test_file_upload_not_allowed_format(self):
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': file}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.count(), 0)
        self.assertEqual(AccountFiles.objects.count(), 0)
        file.close()

    def test_file_upload_not_allowed_size(self):
        file = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        response = self.client.post('/file/upload/', {'video': file}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.count(), 0)
        self.assertEqual(AccountFiles.objects.count(), 0)
        file.close()
    
    
    def test_file_upload_with_invalid_and_valid_file(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.count(), 0)
        self.assertEqual(AccountFiles.objects.count(), 0)
        file1.close()
        file.close()

    
    def test_file_upload_inactive_format(self):
        file = open("filemanager/testFiles/test_640x360.avi", "rb")
        response = self.client.post('/file/upload/', {'video': file}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.count(), 0)
        self.assertEqual(AccountFiles.objects.count(), 0)
        file.close()

    def test_file_upload_with_two_valid_file(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Files.objects.count(), 2)
        self.assertEqual(AccountFiles.objects.count(), 2)
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        file1.close()
        file.close()

    def test_file_upload_with_invalid_duration(self):    
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': file}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        file.close()

class VideoTrimTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(username="testuser", password="testpassword")    
        account = Accounts.objects.create(user=user, nickname="testaccount", is_authenticated=True,
                                           min_duration=1, max_file_size=50, max_duration=300)
        account1 = Accounts.objects.create(user=user, nickname="testaccount1", is_authenticated=True,
                                           min_duration=1, max_file_size=50, max_duration=300)
        format1 = VideoFomats.objects.create(format="mp4")
        format2 = VideoFomats.objects.create(format="avi")
        format3 = VideoFomats.objects.create(format="mkv")  
        account.allowed_formats.add(format1, format2, format3)   
        account.save()
        AccountTokens.objects.create(account=account, token_name="testtoken")
        account1.allowed_formats.add(format1, format2, format3)   
        account1.save()
        AccountTokens.objects.create(account=account1, token_name="testtoken1")
        self.account = account
        self.account1 = account1

    def test_file_trim_valid_file(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        file_count = Files.objects.all().count()
        response = self.client.patch('/file/trim/', data=json.dumps({'video_id': ids[0], 'trim_duration': 13, 'trim_from': "start"}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Files.objects.all().count(), file_count+1)
    
    def test_file_trim_valid_file_invalid_account(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        file_count = Files.objects.all().count()
        response = self.client.patch('/file/trim/', data=json.dumps({'video_id': ids[0], 'trim_duration': 13, 'trim_from': "start"}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)

    def test_file_trim_invalid_methods(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        file_count = Files.objects.all().count()
        self.assertEqual(file_count, 2)
        response = self.client.patch('/file/trim/', {'video_id': ids[0], 'trim_duration': 5, 'trim_from': "start"}, 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        response = self.client.put('/file/trim/', {'video_id': ids[0], 'trim_duration': 5, 'trim_from': "start"}, 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 405)

        response = self.client.post('/file/trim/', {'video_id': ids[0], 'trim_duration': 5, 'trim_from': "start"}, 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 405)
        
        self.assertEqual(Files.objects.all().count(), file_count)

    
    def test_file_trim_invalid_duration(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        file_count = Files.objects.all().count()
        response = self.client.patch('/file/trim/', data=json.dumps({'video_id': ids[0], 'trim_duration': 43, 'trim_from': "start"}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(Files.objects.all().count(), file_count)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch('/file/trim/', data=json.dumps({'video_id': ids[0], 'trim_duration': 39.04, 'trim_from': "start"}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)
        response = self.client.patch('/file/trim/', data=json.dumps({'video_id': ids[0], 'trim_duration': 0, 'trim_from': "start"}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)
        response = self.client.patch('/file/trim/', data=json.dumps({'video_id': ids[0], 'trim_duration': -1, 'trim_from': "start"}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)

class VideoMergeTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(username="testuser", password="testpassword")    
        account = Accounts.objects.create(user=user, nickname="testaccount", is_authenticated=True,
                                           min_duration=1, max_file_size=50, max_duration=300)
        account1 = Accounts.objects.create(user=user, nickname="testaccount1", is_authenticated=True,
                                           min_duration=1, max_file_size=50, max_duration=300)
        format1 = VideoFomats.objects.create(format="mp4")
        format2 = VideoFomats.objects.create(format="avi")
        format3 = VideoFomats.objects.create(format="mkv")  
        account.allowed_formats.add(format1, format2, format3)   
        account.save()
        AccountTokens.objects.create(account=account, token_name="testtoken")
        account1.allowed_formats.add(format1, format2, format3)   
        account1.save()
        AccountTokens.objects.create(account=account1, token_name="testtoken1")
        self.account = account
        self.account1 = account1

    def test_file_merge_valid_file(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test_960x540.mp4", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        file_count = Files.objects.all().count()
        response = self.client.patch('/file/merge/', data=json.dumps({'video_ids': ids}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Files.objects.all().count(), file_count+1)

    def test_file_merge_invalid_account(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        file_count = Files.objects.all().count()
        response = self.client.patch('/file/merge/', data=json.dumps({'video_ids': ids}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)
    
    def test_file_merge_invalid_files(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        file_count = Files.objects.all().count()
        response = self.client.patch('/file/merge/', data=json.dumps({'video_ids': ids + [1]}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(Files.objects.all().count(), file_count)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch('/file/merge/', data=json.dumps({'video_ids': ids + ids}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)
        response = self.client.patch('/file/merge/', data=json.dumps({'video_ids': ids + [None]}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)

        response = self.client.patch('/file/merge/', data=json.dumps({'video_ids': [ids[1]]}), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Files.objects.all().count(), file_count)

class VideoPublicUrlsTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(username="testuser", password="testpassword")    
        account = Accounts.objects.create(user=user, nickname="testaccount", is_authenticated=True,
                                           min_duration=1, max_file_size=50, max_duration=300)
        account1 = Accounts.objects.create(user=user, nickname="testaccount1", is_authenticated=True,
                                           min_duration=1, max_file_size=50, max_duration=300)
        format1 = VideoFomats.objects.create(format="mp4")
        format2 = VideoFomats.objects.create(format="avi")
        format3 = VideoFomats.objects.create(format="mkv")  
        account.allowed_formats.add(format1, format2, format3)   
        account.save()
        AccountTokens.objects.create(account=account, token_name="testtoken")
        account1.allowed_formats.add(format1, format2, format3)   
        account1.save()
        AccountTokens.objects.create(account=account1, token_name="testtoken1")
        self.account = account
        self.account1 = account1

    def test_files_content(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test_960x540.mp4", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        self.assertEqual(Files.objects.all().count(), 2)
        response = self.client.get('/file/urls/?video_ids={}&expire_time=2'.format(",".join(ids)), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 200)

        urls = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(urls.values()), 2)
        stg = Storage(location=settings.MEDIA_ROOT)

        for key, val in urls.items():
            self.assertTrue(key in ids)
            self.assertTrue(val.startswith("http"))
            resp = self.client.get(val)
            
            self.assertEqual(resp.status_code, 200)
            fs_size = stg.size(Files.objects.get(id=key).file_path)
            self.assertEqual(len(resp.content), fs_size)

    def test_file_invalid_account(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        file_count = Files.objects.all().count()
        response = self.client.get('/file/urls/?video_ids={}&expire_time=2'.format(",".join(ids)), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 400)
    
    def test_file_invalid_file_ids(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test1.mkv", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        file_count = Files.objects.all().count()
        self.assertEqual(file_count, 2)
        response = self.client.get('/file/urls/?video_ids={}&expire_time=2'.format(",".join(ids + ['1'])), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/file/urls/?video_ids={}&expire_time=2'.format(",".join(ids + ids)), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)         

        response = self.client.get('/file/urls/?video_ids={}&expire_time=2'.format(",".join(ids + ['null'])), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)


        response = self.client.get('/file/urls/?video_ids=-11111,1&expire_time=2', 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account1.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 400)

    def test_url_expiry(self):
        file1 = open("filemanager/testFiles/test2_5mb.mp4", "rb")
        file = open("filemanager/testFiles/test_960x540.mp4", "rb")
        response = self.client.post('/file/upload/', {'video': [file,file1]}, HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        self.assertEqual(response.status_code, 201)
        file1.close()
        file.close()
        ids = [i.strip() for i in response.content.decode("utf-8").split(":")[1].split(",")]
        self.assertEqual(len(ids), 2)
        
        self.assertEqual(Files.objects.all().count(), 2)
        response = self.client.get('/file/urls/?video_ids={}&expire_time=2'.format(",".join(ids)), 
                                     headers= {'content-type': 'application/json'}, 
                                    HTTP_AUTHORIZATION=f"Bearer {self.account.accounttokens_set.first().access_token}")
        
        self.assertEqual(response.status_code, 200)

        urls = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(urls.values()), 2)
        stg = Storage(location=settings.MEDIA_ROOT)

        resp = self.client.get(urls[ids[0]])
            
        self.assertEqual(resp.status_code, 200)
        fs_size = stg.size(Files.objects.get(id=ids[0]).file_path)
        self.assertEqual(len(resp.content), fs_size)

        time.sleep(3)

        resp = self.client.get(urls[ids[1]])
            
        self.assertEqual(resp.status_code, 400)