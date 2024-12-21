import ffprobe
import os
import uuid
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from filemanager.models import Files, AccountFiles



class FileValidator:
    MAX_FILENAME_LENGTH = 255
    UPLOAD_FOLDER = settings.MEDIA_ROOT

    @staticmethod
    def get_video_duration(video):
        # import pdb; pdb.set_trace()
        duration = -1
        try:
            probe_data = ffprobe.FFProbe(video.temporary_file_path())
            h, m, s = probe_data.metadata['Duration'].split(':')
            duration = int(h) * 3600 + int(m) * 60 + float(s)
            
        except Exception as e:
            print(f"Error getting video duration: {e}")

        return duration

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
        if not min_duration <= FileValidator.get_video_duration(file) <= max_duration:
            raise ValidationError("Invalid video duration")
        
    @staticmethod
    def save_file(file, root_dir=settings.MEDIA_ROOT):
        filename = file.name
        new_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(root_dir, new_filename)
        fs = FileSystemStorage(location=root_dir)
        fs.save(new_filename, file)
        return new_filename, file_path
    
    @staticmethod
    def remove_file(filename, root_dir=settings.MEDIA_ROOT):
        file_path = os.path.join(root_dir, filename)
        os.remove(file_path)
        return True
    
    @staticmethod
    def store_file_metadata(filename, file_path, account):
        file = Files.objects.create(file_name=filename, file_path=file_path)
        AccountFiles.objects.create(account=account, file=file)

    @staticmethod
    def handle_file_upload(request):
        # import pdb; pdb.set_trace()
        account = request.user
        allowed_extensions = [fmt.format for fmt in account.allowed_formats.get_queryset().all()]
        # print(allowed_extensions)
        max_file_size = account.max_file_size * 1024 * 1024 # storing max file size in MB
        file = request.FILES.get('video')
        FileValidator.validate_file(file, allowed_extensions, max_file_size, 
                                    account.min_duration, account.max_duration)
        new_filename, file_path = FileValidator.save_file(file)
        FileValidator.store_file_metadata(new_filename, file_path, account)
        return new_filename