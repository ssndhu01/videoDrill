import ffprobe
import hashlib
import json
import os
import uuid
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from filemanager.models import Files, AccountFiles
from moviepy import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips


class FileValidator:
    MAX_FILENAME_LENGTH = 255
    UPLOAD_FOLDER = settings.MEDIA_ROOT

    @staticmethod
    def get_video_duration(video):
        duration = -1
        try:
            metadata = FileValidator.get_video_metadata(video)
            h, m, s = metadata['Duration'].split(':')
            duration = int(h) * 3600 + int(m) * 60 + float(s)
            
        except Exception as e:
            print(f"Error getting video duration: {e}")

        return duration

    @staticmethod
    def get_video_metadata(file_path):
        metadata = {}
        try:
            probe_data = ffprobe.FFProbe(file_path)
            metadata = probe_data.metadata
        except Exception as e:
            print(f"Error getting video metadata: {e}")

        return metadata
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def validate_file(file, allowed_extensions, max_file_size, min_duration, max_duration):
        if not file:
            raise ValidationError("No video uploaded")
        if file.name == '':
            raise ValidationError("No selected file")
        if not FileValidator.allowed_file(file.name, allowed_extensions):
            raise ValidationError("File type not allowed")
        if len(file.name) > FileValidator.MAX_FILENAME_LENGTH:
            raise ValidationError("Filename too long")
        if file.size > max_file_size:
            raise ValidationError("File too large")
        if not min_duration <= FileValidator.get_video_duration(file.temporary_file_path()) <= max_duration:
            raise ValidationError("Invalid video duration")
        
    @staticmethod
    def save_file(file, root_dir=settings.MEDIA_ROOT):
        filename = file.name
        new_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(root_dir, new_filename)
        fs = FileSystemStorage(location=root_dir)
        fs.save(new_filename, file)
        return file_path
    
    @staticmethod
    def remove_file(filename, root_dir=settings.MEDIA_ROOT):
        file_path = os.path.join(root_dir, filename)
        os.remove(file_path)
        return True

    @staticmethod
    def get_file(file_id):
        return Files.objects.filter(id=file_id).first()
    
    @staticmethod
    def store_file_metadata(filename, file_path, account):
        file = Files.objects.create(file_name=filename, file_path=file_path)
        AccountFiles.objects.create(account=account, file=file)
        return file.id
    
    @staticmethod
    def trim_video(request):
        data = request.data
        file = Files.objects.filter(id=data.get('video_id'))
        if not file.exists():
            raise ValidationError("File does not exist")
        else:
            file = file.first()
        duration = FileValidator.get_video_duration(file.file_path)
        if data['trim_duration'] > duration:
            raise ValidationError("Trim duration exceeds video duration")
        if data['trim_from'] == 'start':
            start = data['trim_duration']
            end = duration
        else:
            start = 0
            end = duration - data['trim_duration']
        clip = VideoFileClip(file.file_path).subclipped(start, end)
        new_filename = f"{uuid.uuid4().hex}_{file.file_name}"
        file_path = os.path.join(settings.MEDIA_ROOT, new_filename) 
        clip.write_videofile(file_path)
        file_id = FileValidator.store_file_metadata(new_filename, file_path, request.user)
        return file_id
    
    @staticmethod
    def merge_videos(request):
        data = request.data
        files = Files.objects.filter(id__in=data.get('video_ids'))
        if len(files) >= 2 and len(files) != len(data.get('video_ids')):
            raise ValidationError("One or more file does not exist")

        # clip = VideoFileClip(file[0].file_path)
        clips = []

        for file in files:
            clips.append(VideoFileClip(file.file_path))

        final_clip = concatenate_videoclips(clips, "compose")
        new_filename = f"{uuid.uuid4().hex}_{files[0].file_name}"
        print(new_filename)
        file_path = os.path.join(settings.MEDIA_ROOT, new_filename) 
        final_clip.write_videofile(file_path)
        file_id = FileValidator.store_file_metadata(new_filename, file_path, request.user)
        return file_id

    @staticmethod
    def handle_file_upload(request):
        account = request.user
        allowed_extensions = [fmt.format for fmt in account.allowed_formats.get_queryset().filter(active=True).all()]
        # print(allowed_extensions)
        max_file_size = account.max_file_size * 1024 * 1024 # storing max file size in MB
        files = request.FILES.getlist('video')
        print(len(files))
        file_ids = []
        for file in files:
            FileValidator.validate_file(file, allowed_extensions, max_file_size, 
                                        account.min_duration, account.max_duration)
            file_path = FileValidator.save_file(file)
            file_ids.append(str(FileValidator.store_file_metadata(file.name, file_path, account)))
        return ",".join(file_ids)
    
    @staticmethod
    def generate_hmac(file_id, start_time, expire_time):
        return hashlib.sha256(f"{file_id}{start_time}{expire_time}{settings.SECRET_KEY}".encode()).hexdigest()

    @staticmethod
    def validate_hmac(params):
        try:
            file_id = params.get('pt', '0')
            start_time = int(params.get('st', 0))
            expire_time = int(params.get('ex', 0))
            current_time = int(datetime.now().timestamp())
            if current_time > start_time + expire_time:
                raise "URL expired"
            return params['__hdna__'] == FileValidator.generate_hmac(file_id, start_time, expire_time)
        except Exception as e:
            raise ValidationError("Invalid URL")   

    @staticmethod
    def generate_public_url(file, expire_time=120):
        # considering expire time as 120 seconds for now - this can be made configurable/input basis
        file_id = file.id
        start_time = int(datetime.now().timestamp())
        hmac = FileValidator.generate_hmac(file_id, start_time, expire_time)

        return f"{settings.MEDIA_URL}?token=pt:{file_id}~st:{start_time}~ex:{expire_time}~__hdna__:{hmac}"

    @staticmethod
    def generate_video_urls(request):
        data = request.GET
        video_ids = data.get('video_ids').split(',')
        files = Files.objects.filter(id__in=video_ids)
        if len(files) != len(video_ids):
            raise ValidationError("One or more file does not exist")

        urls = {}
        for file in files:
            urls[file.id] = FileValidator.generate_public_url(file, data.get('expire_time', 120))

        return json.dumps(urls)