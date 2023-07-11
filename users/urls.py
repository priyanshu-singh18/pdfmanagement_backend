from django.urls import path
from users.views import signup,login

urlpatterns = [
    path('signup', signup),
    path('login' , login)
]
