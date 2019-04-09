from django.shortcuts import render


def index(request):
    return render(request, "frontpage/index.html")
