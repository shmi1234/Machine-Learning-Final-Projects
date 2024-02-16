from django import forms
from projects.models import Question , Answer, Bookmark

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question  # 사용할 모델
        fields = ['subject', 'content', 'image']  # QuestionForm에서 사용할 Question 모델의 속성
        labels = {
            'subject': '제목',
            'content': '내용',
        }
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }

class BookmarkForm(forms.ModelForm):
    class Meta:
        model = Bookmark
        fields = ['search_keyword', 'search_time', 'distance']