from django.http import HttpResponse


def check_out(request):
    return HttpResponse("Logged in")
