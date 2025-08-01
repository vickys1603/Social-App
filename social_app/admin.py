# social_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Custom User model-a register panna
from .models import User, Post, Comment, Follow, Like

# Register your custom User model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Optional: Add custom fields to the admin form if you add them to the User model
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('bio', 'profile_picture',)}),
    # )
    pass # Ippo ethuvum add panna vendam, default UserAdmin-a use pannalam

# Register other models
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username') # author username-a search panna

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    list_filter = ('created_at', 'author', 'post')
    search_fields = ('content', 'author__username', 'post__content')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at', 'follower', 'following')
    search_fields = ('follower__username', 'following__username')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at', 'user', 'post')
    search_fields = ('user__username', 'post__content')