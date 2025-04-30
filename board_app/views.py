from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment, Pet
from .forms import PostForm, CommentForm
from django.db import models

@login_required
def post_list(request):
    pets = Pet.objects.filter(owner=request.user)
    pet_id = request.GET.get('pet')
    posts = Post.objects.filter(pet__owner=request.user)
    
    if pet_id:
        if pet_id == 'all':
            # '함께' 옵션으로 작성된 게시글만 필터링
            posts = posts.filter(is_together=True)
        elif pet_id == 'etc':
            # '기타' 옵션으로 작성된 게시글만 필터링
            posts = posts.filter(is_etc=True)
        else:
            # 개별 반려동물의 게시글이거나, 함께한 게시글 중 해당 반려동물이 포함된 경우
            posts = posts.filter(
                models.Q(pet_id=pet_id) | 
                models.Q(pets__id=pet_id)
            ).distinct()
    
    return render(request, 'board_app/post_list.html', {'posts': posts, 'pets': pets, 'selected_pet_id': pet_id})

@login_required
def post_create(request):
    pets = Pet.objects.filter(owner=request.user)
    if request.method == 'POST':
        selected_pet = request.POST.get('pet')
        # '함께' 선택 시 하나의 게시글 생성하고 여러 반려동물과 연결
        if selected_pet == 'all':
            title = request.POST.get('title')
            content = request.POST.get('content')
            image = request.FILES.get('image')
            # 첫 번째 반려동물을 기본 pet으로 선택
            first_pet = pets.first()
            post = Post.objects.create(
                author=request.user,
                pet=first_pet,
                title=title,
                content=content,
                image=image,
                is_together=True
            )
            # 나머지 반려동물들을 pets 필드에 추가
            post.pets.set(pets)
            messages.success(request, '여러 고양이에 대한 게시글이 작성되었습니다.')
            return redirect('board_app:list')
        # '기타' 선택 시
        elif selected_pet == 'etc':
            title = request.POST.get('title')
            content = request.POST.get('content')
            image = request.FILES.get('image')
            # 첫 번째 반려동물을 기본 pet으로 선택
            first_pet = pets.first()
            post = Post.objects.create(
                author=request.user,
                pet=first_pet,
                title=title,
                content=content,
                image=image,
                is_etc=True
            )
            messages.success(request, '기타 게시글이 작성되었습니다.')
            return redirect('board_app:list')
        # 단일 고양이 선택 시 기존 폼 처리
        form = PostForm(request.POST, request.FILES)
        form.fields['pet'].queryset = pets
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.is_together = False
            post.is_etc = False
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('board_app:detail', post_id=post.id)
    else:
        form = PostForm()
        form.fields['pet'].queryset = pets
    return render(request, 'board_app/post_form.html', {'form': form, 'pets': pets})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, pet__owner=request.user)
    comments = post.comments.all()
    comment_form = CommentForm()
    return render(request, 'board_app/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, pet__owner=request.user)
    if request.method == 'POST':
        data = request.POST.copy()
        if data.get('pet') == 'all':
            first_pet = Pet.objects.filter(owner=request.user).first()
            if first_pet:
                data['pet'] = str(first_pet.id)
        form = PostForm(data, request.FILES, instance=post)
        form.fields['pet'].queryset = Pet.objects.filter(owner=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 수정되었습니다.')
            return redirect('board_app:detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
        form.fields['pet'].queryset = Pet.objects.filter(owner=request.user)
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'board_app/post_form.html', {'form': form, 'post': post, 'pets': pets})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, '게시글이 삭제되었습니다.')
    return redirect('board_app:list')

@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id, pet__owner=request.user)
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
def comment_delete(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id, pet__owner=request.user)
    comment = get_object_or_404(Comment, id=comment_id, post=post, author=request.user)
    comment.delete()
    messages.success(request, '댓글이 삭제되었습니다.')
    return redirect('board_app:detail', post_id=post.id)

@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id, pet__owner=request.user)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()}) 