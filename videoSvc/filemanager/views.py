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
