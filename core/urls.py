from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path("register/", views.register),
    path("login/", views.user_login),
    path("logout/", views.user_logout),
    path("create/", views.create_note),
    path("note/<int:note_id>/", views.note_detail),
    path("search/", views.search),
]