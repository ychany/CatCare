from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment, Pet
from .forms import PostForm, CommentForm

@login_required
def post_list(request):
    pets = Pet.objects.filter(owner=request.user)
    pet_id = request.GET.get('pet')
    posts = Post.objects.filter(author=request.user)
    if pet_id:
        posts = posts.filter(pet_id=pet_id)
    return render(request, 'board_app/post_list.html', {'posts': posts, 'pets': pets, 'selected_pet_id': pet_id})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('board_app:detail', post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'board_app/post_form.html', {'form': form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    return render(request, 'board_app/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 수정되었습니다.')
            return redirect('board_app:detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'board_app/post_form.html', {'form': form, 'post': post})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, '게시글이 삭제되었습니다.')
    return redirect('board_app:list')

@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
    return redirect('board_app:detail', post_id=post.id)

@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()}) 