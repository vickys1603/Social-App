# social_app/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model # Custom User model-a edukka
from django.db import models
from django.utils import timezone # For datetime fields

class User(AbstractUser):
    # Add any additional fields you want for your user profile here.
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Biography")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) # Profile pic storage

    # Idhellam munadi irundha code, change panna thevaiyillai
    # groups = models.ManyToManyField(...)
    # user_permissions = models.ManyToManyField(...)

    def __str__(self):
        return self.username
# Get the custom User model
User = get_user_model() # Idhu namma social_app.User model-a return pannum

# --- Post Model ---
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now) # Post create panna time

    class Meta:
        ordering = ['-created_at'] # Latest posts first

    def __str__(self):
        return f"Post by {self.author.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# --- Comment Model ---
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at'] # Oldest comments first

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

# --- Follow Model ---
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # Oru user oru user-a oru thadava mattum dhaan follow panna mudiyum
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

# --- Like Model ---
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # Oru user oru post-a oru thadava mattum dhaan like panna mudiyum
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"
