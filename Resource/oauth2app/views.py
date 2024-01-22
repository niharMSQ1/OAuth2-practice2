import json
import requests
import uuid
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from oauthlib.common import generate_token
from rest_framework_simplejwt.tokens import RefreshToken as RT
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from oauth2_provider.models import Application, AccessToken, RefreshToken, IDToken
from oauth2_provider.decorators import protected_resource
from django.conf import settings
from django.utils import timezone
from .utils import generate_base64_string

@csrf_exempt
@require_POST
def user_registration(request): # normal django registration
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return JsonResponse({'message': 'User registered successfully.'})
    except IntegrityError:
        return JsonResponse({'message': 'User already registered.'})

@csrf_exempt
@require_POST
def user_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    check_username_exists = User.objects.filter(username=username).exists()
    if check_username_exists:
        password = data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            AccessToken.objects.filter(user=user).delete() # deleting oAuth access token
            RefreshToken.objects.filter(user=user).delete() # deleting oAuth refresh token

            refresh = RT.for_user(user) # creating refresh token using simplejwt so access_token = str(refresh.access_token)

            headers = {
                'Authorization': f'Bearer {str(refresh.access_token)}', # passing access token in headers to call generate token endpoint
            }
            create_oauth_refresh_token = requests.post("http://127.0.0.1:8001/api/generate-token/", headers=headers) # this api is in line no 78(def generate_token_endpoint(request):)

            return JsonResponse({
                "jwt_refresh_token": str(refresh),
                "jwt_access_token": str(refresh.access_token),
                "oauth_refresh_token" : (create_oauth_refresh_token.json())['refresh_token'],
                "oauth_access_token" : (create_oauth_refresh_token.json())['access_token'],
            })
        else:
            return JsonResponse({'message': 'Login unsuccessful.'})
    else:
        return JsonResponse({
            "status": "Failed",
            "message": "matching query does not exist"
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_token_endpoint(request):
    username = request.user.username
    password = request.user.password
    client_id = settings.CLIENT_ID

    try:
        application = Application.objects.get(client_id=client_id)
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Invalid client credentials'}, status=401)

    user = User.objects.get(username=username)
    if user.password == password:
        if user is not None:
            AccessToken.objects.filter(user=user, application=application).delete() # deleting if I am calling the current api separately, otherwise this line is not required
            RefreshToken.objects.filter(user=user, application=application).delete() # deleting if I am calling the current api separately, otherwise this line is not required

            expires = timezone.now() + timezone.timedelta(seconds=3600)
            expires_iso = expires.isoformat()

            new_uuid = uuid.uuid4()
            id_token = IDToken.objects.create(jti=new_uuid, expires=expires)

            access_token = AccessToken.objects.create(
                user=user,
                application=application,
                token=generate_token(),
                expires=expires_iso,
                id_token=id_token,
            )

            refresh_token = RefreshToken.objects.create(
                user=user,
                application=application,
                token=generate_token(),
                access_token=access_token,
            )

            response_data = {
                'access_token': access_token.token,
                'token_type': 'Bearer',
                'expires_in': (expires - timezone.now()).total_seconds(),
                'refresh_token': refresh_token.token,
            }

            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Invalid user credentials'}, status=401)

'''
This particular API has to be called to obtain the new oAuth access token from
the existing oauth refresh token
'''
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_access_token_from_refresh(request):
    try:
        refresh_token = RefreshToken.objects.get(user_id=request.user.id).token # querying the oauth refresh token from JWT access token
        if not refresh_token:
            raise Exception("Refresh token not found")

        access_token_obj = AccessToken.objects.get(pk=(RefreshToken.objects.get(token=refresh_token)).access_token_id) # queyring the oauth access token object from oauth refresh token
        new_access_token = generate_base64_string()  # creating new oauth access token which will update the above oauth access token
        expires_in = timezone.now() + timezone.timedelta(seconds=3600)
        access_token_obj.token = new_access_token
        expires_iso = expires_in.isoformat() # assinging the new oauth access token
        access_token_obj.expires = expires_iso
        access_token_obj.save() # saving the new oauth access token

        return JsonResponse(
            {
                "status": "Success",
                "message": "New access token is been issued",
                "token": new_access_token
            }
        )

    except Exception as ex:
        return JsonResponse({
            "status": "failed",
            "message": str(ex)
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def calling_dummy_api_in_another_project(request):
    url = (json.loads(request.body)).get('url')
    num = (json.loads(request.body)).get('data')
    access_token = (AccessToken.objects.get(user_id=request.user.id)).token
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    post_data = {'data': num}
    post_data_json = json.dumps(post_data)

    calling_inbuilt_3rdparty_api = requests.post("http://127.0.0.1:8001/api/call-3rd-party/", headers=headers, data=post_data_json)

    return JsonResponse(calling_inbuilt_3rdparty_api.json())

@csrf_exempt
@protected_resource()
def calling_3rd_party(request):
    data = json.loads(request.body)
    post_data_json = json.dumps(data)
    calling_project2 = requests.post("http://127.0.0.1:8000/api/dummyApi/", data=post_data_json)
    response_data = calling_project2.json()

    return JsonResponse(
        {
            "status": response_data['status'],
            "message": response_data['message'] 
        }
    )
