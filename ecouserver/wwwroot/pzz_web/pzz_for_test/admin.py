from django.contrib import admin

def index(request):
    return render(request, 'index.html')