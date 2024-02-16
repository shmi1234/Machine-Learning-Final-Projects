from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_question')  # 추천인 추가
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)

    def __str__(self):
        return self.subject

class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')

class Location(models.Model):
    name = models.CharField(max_length=255)
    crime_danger = models.FloatField()
    morning_count = models.FloatField()
    afternoon_count = models.FloatField()
    evening_count = models.FloatField()
    night_count = models.FloatField()
    dawn_count = models.FloatField()

    def __str__(self):
        return self.name
    
class Bookmark(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_bookmark')
    search_keyword = models.CharField(max_length=255)
    search_time = models.CharField(max_length=50)
    distance = models.IntegerField()

    def __str__(self):
        return self.name