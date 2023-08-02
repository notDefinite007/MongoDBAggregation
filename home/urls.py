from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.list_collections),
    path('comments', view=views.list_all_comments),
    path('blogs', view=views.list_all_blogs),
    path('user/<str:username>', view=views.get_details_by_user),
    path('user', view=views.list_all_users),
]
