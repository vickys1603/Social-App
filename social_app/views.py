# social_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from .forms import CustomUserCreationForm, ProfileEditForm, PostForm, CommentForm
from .models import User, Post, Comment, Like, Follow
from django.db.models import Count
# --- Home View (Updated for Feed and Suggested Users with Follow Status) ---
def home_view(request):
    posts_query = Post.objects.all().select_related('author').prefetch_related('likes', 'comments')

    if request.user.is_authenticated:
        # Get users that the current user is following
        following_users_ids = Follow.objects.filter(follower=request.user).values_list('following__id', flat=True)
        # Include current user's own posts in their feed
        posts_query = posts_query.filter(author__id__in=list(following_users_ids) + [request.user.id])

    posts = posts_query.order_by('-created_at')

    posts_with_like_status = []
    for post in posts:
        post.is_liked_by_user = False
        if request.user.is_authenticated:
            post.is_liked_by_user = post.likes.filter(user=request.user).exists()
        posts_with_like_status.append(post)

    # --- New: Suggested Users Logic ---
    suggested_users = []
    if request.user.is_authenticated:
        # Get IDs of users current user is following
        already_following_ids = list(following_users_ids) + [request.user.id]

        # Find users who are not already followed and are not the current user
        # For simplicity, let's just get a few random users for now
        # In a real app, this logic would be more sophisticated (e.g., based on mutual friends, interests)
        all_other_users = User.objects.exclude(id__in=already_following_ids).order_by('?')[:5] # Get 5 random users

        for s_user in all_other_users:
            s_user.is_followed_by_user = False # Default to False
            # No need to check exists() here, as we already excluded followed users
            # This flag is more for consistency if we fetch users differently later
            suggested_users.append(s_user)
    else:
        # If not authenticated, show some random users
        suggested_users = User.objects.all().order_by('?')[:5]


    post_form = PostForm()

    context = {
        'posts': posts_with_like_status,
        'post_form': post_form,
        'suggested_users': suggested_users, # <--- Idha add pannunga
    }
    return render(request, 'social_app/home.html', context)

# --- User Registration View ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Save the new user
            login(request, user) # Log the user in immediately after registration
            return redirect('home') # Redirect to home page or user profile
    else:
        form = CustomUserCreationForm()
    return render(request, 'social_app/register.html', {'form': form})

# --- User Login View ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') # Redirect to home page after login
            else:
                # Optional: Add error message for invalid credentials
                pass
    else:
        form = AuthenticationForm()
    return render(request, 'social_app/login.html', {'form': form})

# --- User Logout View ---
def logout_view(request):
    logout(request)
    return redirect('home') # Redirect to home page after logout
# --- User Profile View ---
@login_required # Idhu user login pannirundha mattum access panna allow pannum
def profile_view(request, username):
    # Requested user-a find pannuvom, illana 404 error throw pannuvom
    user = get_object_or_404(User, username=username)
    # Check if the logged-in user is viewing their own profile
    is_owner = (request.user == user)

    # Optionally, get user's posts, followers, following
    posts = user.posts.all() # From related_name='posts' in Post model
    followers_count = user.followers.count() # From related_name='followers' in Follow model
    following_count = user.following.count() # From related_name='following' in Follow model

    # Check if the logged-in user is already following this profile
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = user.followers.filter(follower=request.user).exists()


    context = {
        'user_profile': user,
        'is_owner': is_owner,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    }
    return render(request, 'social_app/profile.html', context)

# --- Profile Edit View ---
@login_required
def profile_edit_view(request):
    # Only the logged-in user can edit their own profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user) # request.FILES for image uploads
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username) # Redirect to updated profile
    else:
        form = ProfileEditForm(instance=request.user) # Pre-fill form with current user data
    return render(request, 'social_app/profile_edit.html', {'form': form})





# --- Create Post View ---
@login_required
@require_POST # Idhu POST requests-a mattum accept pannum
def create_post(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False) # Object-a create pannum, aana save pannaadhu
        post.author = request.user # Current logged-in user-a author-a set pannuvom
        post.save() # Ippo save pannuvom
        return redirect('home') # Post create aanadhum home page-ku redirect
    # If form is not valid, maybe redirect back to home with errors or render form again
    return redirect('home') # For simplicity, redirect back to home

# --- Like/Unlike Post View (API Endpoint) ---
@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if not post_id:
        return JsonResponse({'status': 'error', 'message': 'Post ID is required.'}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    try:
        # Check if user already liked the post
        like = Like.objects.get(post=post, user=user)
        like.delete() # Unlike the post
        liked = False
    except Like.DoesNotExist:
        # If not liked, create a new like
        Like.objects.create(post=post, user=user)
        liked = True

    # Return updated like count
    likes_count = post.likes.count()
    return JsonResponse({'status': 'success', 'liked': liked, 'likes_count': likes_count})

# --- Add Comment View (API Endpoint) ---
@login_required
@require_POST
def add_comment(request):
    post_id = request.POST.get('post_id')
    content = request.POST.get('content')

    if not post_id or not content:
        return JsonResponse({'status': 'error', 'message': 'Post ID and content are required.'}, status=400)

    post = get_object_or_404(Post, id=post_id)

    comment_form = CommentForm({'content': content}) # Create form with submitted content
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

        # Return new comment data for frontend to display
        return JsonResponse({
            'status': 'success',
            'comment_id': comment.id,
            'author_username': comment.author.username,
            'comment_content': comment.content,
            'created_at': comment.created_at.strftime("%b %d, %Y %H:%M"), # Format datetime
            'comments_count': post.comments.count(),
        })
    else:
        return JsonResponse({'status': 'error', 'message': comment_form.errors.as_json()}, status=400)

# --- Post Detail View (Optional, for single post page) ---
def post_detail_view(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('likes', 'comments'), id=post_id)
    comments = post.comments.all().select_related('author')
    comment_form = CommentForm()

    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(user=request.user).exists() # This logic is already correct here

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
    }
    return render(request, 'social_app/post_detail.html', context)


# --- Follow/Unfollow User View (API Endpoint) ---
@login_required
@require_POST
def follow_toggle(request):
    user_id_to_follow = request.POST.get('user_id')
    if not user_id_to_follow:
        return JsonResponse({'status': 'error', 'message': 'User ID is required.'}, status=400)

    target_user = get_object_or_404(User, id=user_id_to_follow)
    current_user = request.user

    # User themselves-a follow panna mudiyadhu
    if current_user == target_user:
        return JsonResponse({'status': 'error', 'message': "You cannot follow yourself."}, status=400)

    followed = False
    try:
        # Check if current_user already follows target_user
        follow_instance = Follow.objects.get(follower=current_user, following=target_user)
        follow_instance.delete() # Unfollow
        followed = False
    except Follow.DoesNotExist:
        # If not following, create a new Follow instance
        Follow.objects.create(follower=current_user, following=target_user)
        followed = True

    # Return updated follower/following counts for target user
    followers_count = target_user.followers.count()
    following_count = target_user.following.count() # This is for the target user's 'following' count, not the current user's.
                                                    # If you need current user's following count, fetch it separately.

    return JsonResponse({
        'status': 'success',
        'followed': followed,
        'followers_count': followers_count,
        # 'current_user_following_count': current_user.following.count() # Optional: if you need to update current user's following count on frontend
    })
