from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@cache_page(60, key_prefix='index_page')
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


@cache_page(60, key_prefix='profile_page')
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_profile = author.posts.all().order_by('-pub_date')
    posts_count = posts_profile.count()
    paginator = Paginator(posts_profile, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        following = Follow.objects.get(user=request.user, author=author)
    except Exception:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


@cache_page(60 * 5, key_prefix='post_detail_page')
def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    selected_post = get_object_or_404(Post, id=post_id)
    author = selected_post.author
    posts_count = author.posts.count()
    context = {'selected_post': selected_post,
               'author': author,
               'posts_count': posts_count,
               'form': CommentForm,
               'comments': selected_post.comments.all()
               }
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user.username)
        return render(request, 'posts/post_create.html', {'form': form})
    form = PostForm
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id, author=request.user)
    is_edit = True
    if request.user == edit_post.author:
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=edit_post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(request, 'posts/post_create.html', {
            'form': form,
            'is_edit': is_edit,
            'post_id': post_id
        })
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id,)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
@cache_page(20, key_prefix='index_follow')
def follow_index(request):
    follow_post = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(follow_post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow_author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=follow_author).delete()
    return redirect('posts:profile', username=username)
