from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User
from .forms import PostForm
from .utils import create_paginator


INDEX_POSTS_LIMIT = 10
GROUP_POSTS_LIMIT = 10
PROFILE_POSTS_LIMIT = 10


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = create_paginator(request, posts, INDEX_POSTS_LIMIT)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = create_paginator(request, posts, GROUP_POSTS_LIMIT)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = create_paginator(request, posts, PROFILE_POSTS_LIMIT)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST)
    context = {
        'form': form,
    }
    if not form.is_valid():
        return render(request, template, context)
    if request.POST:
        post = form.save(commit=False)
        post.author = request.user
        post.save()
    return redirect('posts:profile', request.user.username)


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        form = PostForm(request.POST)
        context = {
            'post': post,
            'is_edit': True,
            'form': form,
        }
        if not form.is_valid():
            return render(request, template, context)
        post = form.save(commit=False)
        post.author = request.user
        post.save()
    return redirect('posts:post_detail', post_id)
