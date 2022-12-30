from django.shortcuts import render,HttpResponse
from users.forms import UserRegistrationForm

def index(request):
    return render(request,'index.html',{})

def logout(request):
    return render(request,'index.html',{})

def UserRegister(request):
    form = UserRegistrationForm()
    return render(request,'Register.html',{'form':form})