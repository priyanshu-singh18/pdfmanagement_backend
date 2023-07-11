from django.urls import path
from uploads.views import upload_file, fetch_file, shared_files,share_file, post_comment, fetch_comments

urlpatterns = [
    path('upload', upload_file),
    path('fetch', fetch_file),
    path('shared', shared_files),
    path('share',share_file),
    path('comment', post_comment),
    path('comments', fetch_comments)
]
