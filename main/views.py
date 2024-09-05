from django.shortcuts import render
from django.http import HttpResponse


def articles(request):
    return HttpResponse("Hello, world.")

# Create your views here.
