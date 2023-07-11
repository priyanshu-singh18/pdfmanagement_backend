from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from uploads.models import Upload,Comments
from users.models import UserModel
import base64,json
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from rest_framework import status
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request, **kwargs):
    try:
        parser_classes = [MultiPartParser, FileUploadParser, FormParser]
        
        file = request.FILES['file']

        if file.content_type != 'application/pdf':
            return Response({"error":"Invalid file type. Only PDF files are allowed."}, status=400)
        
        file = file.read()
        
        dummy_email = request.user
        
        try:
            user = UserModel.objects.get(username=dummy_email.username)
        except ObjectDoesNotExist:
            return Response({"error":"User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        Upload.objects.create(uploaded_by_id=user, uploaded_file=file, uploaded_by_email=dummy_email.username)
        
        return Response("Working upload" , status=status.HTTP_201_CREATED)
    
    except KeyError:
        return Response({"error":"File not found in request"}, status=400)
    
    except Exception as e:
        return Response({"error":str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_file(request, **kwargs):
    try:
        user_email = request.user
        data = Upload.objects.filter(uploaded_by_email = user_email)
    
    
        responseList=[]
        for x in data:
            del x.__dict__['_state']
            file_data = x.__dict__['uploaded_file']
            data = base64.b64encode(file_data)
            x.__dict__['uploaded_file'] = data
            responseList.append(x.__dict__)

        return Response(responseList, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shared_files(request, **kwargss):
    try:
        user_email = request.user.username
        
        if not user_email:
            return Response({"error" :"Error in finding user"},status=status.HTTP_404_NOT_FOUND)
        
        user = UserModel.objects.filter(username=user_email)
        
        response = []
        if user[0].access_shared_ids is None:
            return Response([])
    
        for file_id in user[0].access_shared_ids:
            try:
                obj = Upload.objects.get(file_id=file_id)
                if not obj:
                    continue
                del obj.__dict__['_state']
                data = base64.b64encode(obj.__dict__['uploaded_file'])
                obj.__dict__['uploaded_file'] = data
                response.append(obj.__dict__)
            except ObjectDoesNotExist:
                continue
    
        return Response(response ,status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error":"An error occurred: " + str(e)},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_file(request, **kwargss):   
    try:
        share_to = request.data['share_to']
        file_id = request.data['file_id']
    except KeyError:
        return Response({"error":"Missing 'share_to' or 'file_id' in request data"}, status=400)
    
    file = Upload.objects.get(file_id=file_id)
    if file.uploaded_by_email== share_to:
        return Response({"error":"The recipient is the owner of the file you are sharing"},status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = UserModel.objects.get(username=share_to)
    except UserModel.DoesNotExist:
        return Response({"error":"Recipient email isnt registered on PDF management & collab."}, status=404)
    
    if user.username == request.user.username:
        return Response({"error":"You cannot share your own file"}, status=400)
    
    
    if len(user.access_shared_ids)>0:
        for x in user.access_shared_ids:
            if x == file_id:
                return Response({"error" : "The recipient already has the access of the file you are Sharing"},status=status.HTTP_403_FORBIDDEN)

    user.access_shared_ids.append(file_id)
    user.save()
    # print(user.access_shared_ids)

    return Response({"message":f"File with FileID:{file_id} shared."} ,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_comment(request,**kwargs):
    try:
        user_email = request.user.username
        file_id = request.data.get('file_id')
        parent_id = request.data.get('parent_id', None)
        content = request.data.get('content')
        
        user = UserModel.objects.get(username=user_email)
        file = Upload.objects.get(file_id=file_id)
        
        comment = Comments(author=user, content=content, author_email=user_email, post=file)
        
        if parent_id is not None:
            comment.parent_id_id = parent_id
            
        comment.save()

        return Response("Comment Saved")
    
    except ObjectDoesNotExist:
        return Response({"error":"User or File not found"}, status=404)
    
    except Exception as e:
        return Response(str(e), status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_comments(request,**kwargs):
    try:
        file_id = request.GET.get('file_id', '')
        if not file_id:
            raise ValidationError({"error":'file_id parameter is missing'},status=status.HTTP_400_BAD_REQUEST)

        comments = Comments.objects.filter(parent_id=None, post=file_id)

        comment_list = []
        for comment in comments:
            comment_data = {
                'comment_id': comment.comment_id,
                'content': comment.content,
                'author': comment.author.username,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'replies': []
            }

            replies = Comments.objects.filter(parent_id=comment.comment_id)
            for reply in replies:
                reply_data = {
                    'comment_id': reply.comment_id,
                    'content': reply.content,
                    'author': reply.author.username,
                    'timestamp': reply.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
                comment_data['replies'].append(reply_data)

            comment_list.append(comment_data)

        return Response({'comments': comment_list})

    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
