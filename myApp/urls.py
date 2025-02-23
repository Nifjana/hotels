from django.urls import path
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('about-us/', views.about1, name='about-us'),
    path('users/', views.create_user, name='users'),
    path('owner/',views.create_owner, name='owner' ),
    path('user-login/', views.user_login, name='user_login'),
    path('owner-login/', views.owner_login, name='owner_login'),
    path('dashboard_owner/', views.dashboard_owner, name='dashboard_owner'),
    path('dashboard-user/', views.dashboard_user, name='dashboard_user'),
    path('logout/', views.user_logout, name='logout'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
]