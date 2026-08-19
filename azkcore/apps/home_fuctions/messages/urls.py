from django.urls import path
from . import views

urlpatterns = [
    path('', views.messages_view, name='messages'),
    #path('messages/<int:pk>/atendido/', views.contact_message_mark_atendido, name='contact_message_mark_atendido'),
]