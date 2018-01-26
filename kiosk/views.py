from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, Kiosk")


def logged_in(request):
    return HttpResponse("Logged in")
