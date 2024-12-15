from django.urls import path
from .views import RegisterView, LoginView, SendMessageView, ReceiveMessageView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("send_message/", SendMessageView.as_view(), name="send_message"),
    path("receive_message/", ReceiveMessageView.as_view(), name="receive_message"),
]
