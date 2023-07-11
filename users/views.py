from users.models import UserModel
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password,make_password
from django.core.exceptions import ObjectDoesNotExist,ValidationError



@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        username = request.data.get('username')
        name = request.data.get('name')
        password = request.data.get('password')

        if not username or not name or not password:
            return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.get(username=username)
            return Response({"error": "You are already registered"}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.create(username=username, name=name)
                user.set_password(password)
                user.is_superuser = False
                user.save()
                refresh = RefreshToken.for_user(user)

                return Response({"message": "Account created successfully", "Token": str(refresh.access_token),
                                 "Refresh_Token": str(refresh)}, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "An error occurred while saving the user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login(request,**kwargs):
    if request.method == 'POST':
        try:
            username = request.data['username']
            password = request.data['password']

            user = UserModel.objects.get(username=username)
            haspassword = user.password

            if check_password(password, haspassword):
                user = authenticate(username=username, password=password)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successfully",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                })
            else:
                return Response({"error": "Incorrect password. Forgot?"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response({"error": "This username is not registered yet"}, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError:
            return Response({"error": "Missing username or password in the request"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)