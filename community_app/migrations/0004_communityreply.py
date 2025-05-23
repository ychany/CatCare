# Generated by Django 5.2 on 2025-04-30 06:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_app', '0003_communitycomment_likes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='내용')),
                ('is_anonymous', models.BooleanField(default=False, verbose_name='익명 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='작성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_replies', to=settings.AUTH_USER_MODEL, verbose_name='작성자')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='community_app.communitycomment', verbose_name='댓글')),
                ('likes', models.ManyToManyField(blank=True, related_name='liked_community_replies', to=settings.AUTH_USER_MODEL, verbose_name='좋아요')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='community_app.communityreply', verbose_name='부모 대댓글')),
            ],
            options={
                'verbose_name': '대댓글',
                'verbose_name_plural': '대댓글들',
                'ordering': ['created_at'],
            },
        ),
    ]
