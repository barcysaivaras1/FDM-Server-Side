from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.http import HttpResponse

class RegisterView(APIView):
    def post(self, request):
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            User.objects.create_user(username, email, password)
            return HttpResponse("Successfully created a user")

        return HttpResponse("User with that username already exists")
        

class LoginView(APIView):
    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse("No user found with that username")

        return HttpResponse("You're logged in")