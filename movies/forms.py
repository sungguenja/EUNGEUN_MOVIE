from django import forms
from .models import Article, Comment

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'rank', 'content']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'col-12 form-control', 'placeholder': '리뷰제목을 입력해주세요'}),
            'rank': forms.Select(choices=[[i,i] for i in range(0,11)]),
            'content' : forms.Textarea(attrs={'class':'col-12 form-control', 'placeholder':'내용을 입력해주세요','cols':100, 'rows':10})
        }
        labels = {
            'title': ('리뷰 제목'),
            'rank': ('별점'),
            'content': ('내용'),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': '댓글을 입력해주세요!', 'rows':3})
        }
        labels = {
            'content': ('')
        }