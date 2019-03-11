from django.shortcuts import render


def index(request):
    return render(request, "front_page/index.html")
