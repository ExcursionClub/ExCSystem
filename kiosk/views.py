from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, Kiosk")


def check_out(request):
    return HttpResponse("Logged in")
