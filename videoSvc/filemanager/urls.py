from django.urls import path
# from rest_framework.routers import DefaultRouter
from .views import UploadFileView

urlpatterns = [
    path("upload/", UploadFileView.as_view(), name="file_upload"),
]


# route = DefaultRouter(trailing_slash=False)

# route.register(r'upload', UploadFileView, base_name='file_upload')

# urlpatterns = [
#         url(r'^', include(route.urls)),
# ]