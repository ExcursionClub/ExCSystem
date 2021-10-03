from django.shortcuts import render, redirect


def index(request):
    return redirect('https://sites.uw.edu/climb')
    # return render(request, "frontpage/index.html")
