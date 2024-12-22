from django.http import HttpResponse
from filemanager.validations import FileValidator
from django.views import View
from django.core.exceptions import ValidationError
from videoSvc.auth import CustomTokenAuthentication

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class UploadFileView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace()
        if 'video' not in request.FILES:
            return HttpResponse("No file uploaded", status=400) 
        
        try:
            file_id = FileValidator.handle_file_upload(request)
            # Handle file saving here
            return HttpResponse("File uploaded successfully with id : " + str(file_id), status=201)
        except ValidationError as e:
            return HttpResponse(f"File validation failed: {e}", status=400)


class TrimFileView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data = request.data
        video_name = data.get('video_id')
        trim_duration = data.get('trim_duration')
        trim_from = data.get('trim_from')

        if not video_name or not trim_duration or not trim_from:
            return HttpResponse("Missing required parameters", status=400)

        if trim_from not in ['start', 'end']:
            return HttpResponse("Invalid value for trim_from. Must be 'start' or 'end'", status=400)

        try:
            trim_duration = int(trim_duration)
            if trim_duration <= 0:
                raise ValueError
        except ValueError:
            return HttpResponse("Invalid trim_duration. Must be a positive integer", status=400)
        
        try:
            trimmed_video = FileValidator.trim_video(request)
            # Handle file saving here
            return HttpResponse("File trimmed successfully with id : " + str(trimmed_video), status=200)
        except ValidationError as e:
            return HttpResponse(f"File validation failed: {e}", status=400)
        

class MergeFileView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data = request.data
        video_ids = data.get('video_ids')

        if not video_ids:
            return HttpResponse("Missing required parameters", status=400)

        try:
            merged_video = FileValidator.merge_videos(request)
            # Handle file saving here
            return HttpResponse("File merged successfully with id : " + str(merged_video), status=200)
        except ValidationError as e:
            return HttpResponse(f"File validation failed: {e}", status=400)


class GenerateFileURLView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = request.GET
        video_ids = data.get('video_ids')
        expiry = data.get('expire_time')

        if not video_ids and not expiry and expiry <= 1 and expiry >= 86400: # putting max limit of 1 day for now - can be configurable
            return HttpResponse("Missing required parameters", status=400)

        try:
            video_urls = FileValidator.generate_video_urls(request)
            # Handle file saving here
            return HttpResponse(video_urls, status=200)
        except ValidationError as e:
            return HttpResponse(f"File validation failed: {e}", status=400)


class DownloadFileView(APIView):

    def get(self, request, *args, **kwargs):
        hmac_sign = request.GET.get('token')
        if not hmac_sign:
            return HttpResponse("Missing required parameters", status=400)
        
        try:
            params = {i.split(":")[0]: i.split(":")[1] for i in hmac_sign.split('~')}
            if not FileValidator.validate_hmac(params):
                return HttpResponse("Invalid token", status=400)
            file = FileValidator.get_file(params['pt'])  # pt is the file id in the token
            with open(file.file_path, 'rb') as video:
                response = HttpResponse(video.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = 'inline; filename=' + file.file_name
                return response
        except ValidationError as e:
            return HttpResponse(f"File validation failed: {e}", status=400)
        except FileNotFoundError:
            return HttpResponse("File not found", status=404)