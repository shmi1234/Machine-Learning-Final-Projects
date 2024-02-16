from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from ..models import Question

def page(request):
    return render(request, 'projects/page.html')

def data(request) :
    return render(request,'projects/data.html')

def about(request):
    return render(request,'projects/about.html')