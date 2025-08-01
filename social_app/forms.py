# social_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Post, Comment # Post and Comment-a import pannunga

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

# --- New: Post Form ---
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content'] # User content mattum input vaanguvom
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': "What's on your mind?"}),
        }

# --- New: Comment Form ---
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content'] # Comment content mattum input vaanguvom
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': "Add a comment...", 'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-1 focus:ring-blue-300 focus:border-transparent'}),
        }