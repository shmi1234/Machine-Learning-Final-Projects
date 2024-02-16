from django.contrib import admin
from .models import Question
from .models import Location

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Question, QuestionAdmin)
admin.site.register(Location)
