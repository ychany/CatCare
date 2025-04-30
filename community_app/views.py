from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import CommunityPost, CommunityComment, CommunityReply
from .forms import CommunityPostForm, CommunityCommentForm, CommunityReplyForm
from django.http import JsonResponse

def post_list(request):
    posts = CommunityPost.objects.all()
    
    # 기간 필터링
    period = request.GET.get('period', '')
    if period:
        now = timezone.now()
        if period == '1d':
            posts = posts.filter(created_at__gte=now - timedelta(days=1))
        elif period == '1w':
            posts = posts.filter(created_at__gte=now - timedelta(weeks=1))
        elif period == '1m':
            posts = posts.filter(created_at__gte=now - timedelta(days=30))
        elif period == '6m':
            posts = posts.filter(created_at__gte=now - timedelta(days=180))
        elif period == '1y':
            posts = posts.filter(created_at__gte=now - timedelta(days=365))
    
    # 날짜 범위 필터링
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        posts = posts.filter(created_at__range=[start_date, end_date])
    
    # 검색
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    return render(request, 'community_app/post_list.html', {
        'posts': posts,
        'search_query': search_query,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('community_app:detail', post_id=post.id)
    else:
        form = CommunityPostForm()
    return render(request, 'community_app/post_form.html', {'form': form})

def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    post.views += 1
    post.save()
    
    comments = post.comments.all()
    comment_form = CommunityCommentForm()
    
    return render(request, 'community_app/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, author=request.user)
    if request.method == 'POST':
        form = CommunityPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 수정되었습니다.')
            return redirect('community_app:detail', post_id=post.id)
    else:
        form = CommunityPostForm(instance=post)
    return render(request, 'community_app/post_form.html', {'form': form, 'post': post})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, author=request.user)
    post.delete()
    messages.success(request, '게시글이 삭제되었습니다.')
    return redirect('community_app:list')

@login_required
def comment_create(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    if request.method == 'POST':
        form = CommunityCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
    return redirect('community_app:detail', post_id=post.id)

@login_required
def comment_delete(request, post_id, comment_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comment = get_object_or_404(CommunityComment, id=comment_id, post=post, author=request.user)
    comment.delete()
    messages.success(request, '댓글이 삭제되었습니다.')
    return redirect('community_app:detail', post_id=post.id)

@login_required
def post_like(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})

@login_required
def comment_like(request, post_id, comment_id):
    comment = get_object_or_404(CommunityComment, id=comment_id, post_id=post_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': comment.likes.count()})

@login_required
def reply_create(request, post_id, comment_id):
    comment = get_object_or_404(CommunityComment, id=comment_id, post_id=post_id)
    if request.method == 'POST':
        form = CommunityReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                reply.parent_id = parent_id
            reply.save()
            messages.success(request, '답글이 작성되었습니다.')
    return redirect('community_app:detail', post_id=post_id)

@login_required
def reply_delete(request, post_id, comment_id, reply_id):
    reply = get_object_or_404(CommunityReply, id=reply_id, comment_id=comment_id, author=request.user)
    reply.delete()
    messages.success(request, '답글이 삭제되었습니다.')
    return redirect('community_app:detail', post_id=post_id)

@login_required
def reply_like(request, post_id, comment_id, reply_id):
    reply = get_object_or_404(CommunityReply, id=reply_id, comment_id=comment_id)
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
        liked = False
    else:
        reply.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': reply.likes.count()})
