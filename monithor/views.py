from django.shortcuts import render
from django.http import HttpResponse

def settings_view(request):
    return render(request, 'settings.html')

def index_view(request):
    items1 = ["Item 1A", "Item 1B", "Item 1C"]
    items2 = ["Item 2A", "Item 2B", "Item 2C"]
    return render(request, 'lists.html', {'list1': items1, 'list2': items2})
