from django.shortcuts import render

# Create your views here.
def todo(request) : 
    return render(request, 'dashboard/todo.html')