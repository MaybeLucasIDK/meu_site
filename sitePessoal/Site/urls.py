from django.urls import path
from . import views

app_name = 'Site'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('gallery/', views.gallery, name='gallery'),
    path('api/create-chat/', views.create_chat_room, name='create_chat_room'),
    
    # Admin URLs
    path('chat/admin/', views.admin_chat_list, name='admin_chat_list'),
    path('chat/admin/<uuid:room_uuid>/', views.admin_chat_room, name='admin_chat_room'),
    path('chat/admin/delete/<uuid:room_uuid>/', views.admin_delete_chat_room, name='delete_chat_room'),
]

