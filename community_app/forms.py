from django import forms
from .models import CommunityPost, CommunityComment, CommunityReply

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'is_anonymous', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
        }

class CommunityCommentForm(forms.ModelForm):
    class Meta:
        model = CommunityComment
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class CommunityReplyForm(forms.ModelForm):
    class Meta:
        model = CommunityReply
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': '답글을 입력하세요...'}),
        } 