from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Post, Group, User
from .forms import PostForm


INDEX_POSTS_LIMIT = 10
GROUP_POSTS_LIMIT = 10


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = User.objects.get(username=username)
    posts = (Post.objects.select_related('author').select_related('group')
             .filter(author=author))
    count = posts.aggregate(Count("id"))
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'count': count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = (Post.objects.select_related('author').select_related('group')
            .filter(id=post_id))[0]
    title = post.text[:30]
    author = post.author
    count = Post.objects.filter(author=author).aggregate(Count("id"))
    context = {
        'post': post,
        'title': title,
        'author': author,
        'count': count,
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
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = (Post.objects.select_related('author').select_related('group')
            .filter(id=post_id))[0]
    form = PostForm(request.POST)
    if post.author == request.user:
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
    else:
        return redirect('posts:post_detail', post_id)
