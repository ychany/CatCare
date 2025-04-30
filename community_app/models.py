from django.db import models
from django.contrib.auth.models import User

class CommunityPost(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts', verbose_name='작성자')
    is_anonymous = models.BooleanField(default=False, verbose_name='익명 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    views = models.PositiveIntegerField(default=0, verbose_name='조회수')
    likes = models.ManyToManyField(User, related_name='liked_community_posts', blank=True, verbose_name='좋아요')
    image = models.ImageField(upload_to='community/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '커뮤니티 게시글'
        verbose_name_plural = '커뮤니티 게시글들'

    def __str__(self):
        return self.title

    def get_author_name(self):
        return '익명' if self.is_anonymous else self.author.username

class CommunityComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments', verbose_name='게시글')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments', verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    is_anonymous = models.BooleanField(default=False, verbose_name='익명 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    likes = models.ManyToManyField(User, related_name='liked_community_comments', blank=True, verbose_name='좋아요')

    class Meta:
        ordering = ['created_at']
        verbose_name = '댓글'
        verbose_name_plural = '댓글들'

    def __str__(self):
        return f"{self.get_author_name()}의 댓글"

    def get_author_name(self):
        return '익명' if self.is_anonymous else self.author.username

class CommunityReply(models.Model):
    comment = models.ForeignKey(CommunityComment, on_delete=models.CASCADE, related_name='replies', verbose_name='댓글')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_replies', verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    is_anonymous = models.BooleanField(default=False, verbose_name='익명 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    likes = models.ManyToManyField(User, related_name='liked_community_replies', blank=True, verbose_name='좋아요')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name='부모 대댓글')

    class Meta:
        ordering = ['created_at']
        verbose_name = '대댓글'
        verbose_name_plural = '대댓글들'

    def __str__(self):
        return f"{self.get_author_name()}의 대댓글"

    def get_author_name(self):
        return '익명' if self.is_anonymous else self.author.username
