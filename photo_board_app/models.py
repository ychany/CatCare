from django.db import models
from django.contrib.auth.models import User
from common_app.models import Pet

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='작성자')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='posts', verbose_name='반려동물')
    pets = models.ManyToManyField(Pet, related_name='together_posts', verbose_name='함께한 반려동물들', blank=True)
    image = models.ImageField(upload_to='post_images/', verbose_name='이미지')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name='좋아요')
    is_together = models.BooleanField(default=False, verbose_name='함께 작성')
    is_etc = models.BooleanField(default=False, verbose_name='기타 작성')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '게시글'
        verbose_name_plural = '게시글들'

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='게시글')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['created_at']
        verbose_name = '댓글'
        verbose_name_plural = '댓글들'

    def __str__(self):
        return f"{self.author.username}의 댓글" 