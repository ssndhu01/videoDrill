from django.http import HttpResponse
from filemanager.validations import FileValidator
from django.views import View
from django.core.exceptions import ValidationError
from videoSvc.auth import CustomTokenAuthentication

from rest_framework.views import APIView


# Create your views here.
class UploadFileView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'video' not in request.FILES:
            return HttpResponse("No file uploaded", status=400) 
        
        try:
            FileValidator.handle_file_upload(request)
            # Handle file saving here
            return HttpResponse("File uploaded successfully")
        except ValidationError as e:
            return HttpResponse(f"File validation failed: {e}", status=400)
