from django.urls import path
from . import views

urlpatterns = [
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('search/', views.search, name='search'),
    path('crash/', views.crash, name='crash'),
    path('fetch/', views.fetch_external, name='fetch_external'),
]