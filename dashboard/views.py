from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from cryptography.fernet import Fernet  # Import Fernet for encryption/decryption
from django.conf import settings  # Import settings to access SHARED_SECRET_KEY
import requests  # Ensure that requests is imported for the message sending functionality


# Registration View
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create user and set hashed password
        user = User.objects.create(username=username, password=make_password(password))
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


# Login View using JWT (this is using default TokenObtainPairView from SimpleJWT)
class LoginView(TokenObtainPairView):
    # This will generate the JWT for login automatically using SimpleJWT's functionality
    pass


# Send Message View (Encrypt message before sending)
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can send messages

    def post(self, request):
        message = request.data.get("message")
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Encrypt the message using the shared secret key
        cipher_suite = Fernet(settings.SHARED_SECRET_KEY)
        encrypted_message = cipher_suite.encrypt(message.encode())

        # Send encrypted message to Service2
        response = requests.post(
            "http://127.0.0.1:8002/api/receive_message/",  # URL of Service2's receive endpoint
            json={"encrypted_message": encrypted_message.decode()},
        )

        return Response({"service2_response": response.json()})

# Receive Message View (Decrypt message)
class ReceiveMessageView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can receive messages

    def post(self, request):
        encrypted_message = request.data.get("encrypted_message")
        if not encrypted_message:
            return Response({"error": "Encrypted message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Decrypt the message using the shared secret key
        cipher_suite = Fernet(settings.SHARED_SECRET_KEY)
        decrypted_message = cipher_suite.decrypt(encrypted_message.encode()).decode()

        return Response({"decrypted_message": decrypted_message})


# Token Refresh View (using the default TokenRefreshView from SimpleJWT)
class TokenRefreshView(TokenRefreshView):
    pass
