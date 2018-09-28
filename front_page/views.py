from django.shortcuts import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template('front_page/index.html')
    context = {}
    return HttpResponse(template.render(context, request))
