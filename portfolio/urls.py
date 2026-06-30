from django.urls import path
from .views import ChatView, ContactSubmitView, IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('contact/submit/', ContactSubmitView.as_view(), name='contact_submit'),
    path('api/chat/', ChatView.as_view(), name='chat'),
]
