from django.shortcuts import render  # type: ignore

def homePrincipal(request): return render(request,'home.html')

def menu(request): return render(request,'menu.html')
