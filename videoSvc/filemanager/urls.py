from django.urls import path
# from rest_framework.routers import DefaultRouter
from .views import UploadFileView, TrimFileView, MergeFileView, DownloadFileView, GenerateFileURLView

urlpatterns = [
    path("upload/", UploadFileView.as_view(), name="file_upload"),
    path("trim/", TrimFileView.as_view(), name="file_trim"),
    path("merge/", MergeFileView.as_view(), name="file_merge"),
    path("public/", DownloadFileView.as_view(), name="file_download"),
    path("urls/", GenerateFileURLView.as_view(), name="file_urls"),
]


# route = DefaultRouter(trailing_slash=False)

# route.register(r'upload', UploadFileView, base_name='file_upload')

# urlpatterns = [
#         url(r'^', include(route.urls)),
# ]