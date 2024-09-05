from django.shortcuts import render
from django.http import HttpResponse


def articles(request):
	context = {}
	return render(request, "main/articles.html", context)


def reviews(request):
	context = {}
	return render(request, "main/reviews.html", context)


def about(request):
	context = {}
	return render(request, "main/about.html", context)

