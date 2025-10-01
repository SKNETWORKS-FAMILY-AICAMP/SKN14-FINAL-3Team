from django.shortcuts import render

# Create your views here.
def kb_bank(request) : 
    return render(request, 'user/main.html')