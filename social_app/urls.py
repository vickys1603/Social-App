# social_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),

    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('post/like/', views.like_post, name='like_post'),
    path('post/comment/', views.add_comment, name='add_comment'),

    # --- New: Follow/Unfollow URL ---
    path('follow_toggle/', views.follow_toggle, name='follow_toggle'), # AJAX endpoint for follow/unfollow
]