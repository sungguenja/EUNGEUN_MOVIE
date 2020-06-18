from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
# Create your views here.
User = get_user_model()
def signup(request):
    if request.user.is_authenticated:
        messages.warning(request,'로그인 상태입니다. 로그아웃하고 이용해주세요! 😁')
        return redirect('movies:index')
    else:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                auth_login(request,user,backend='django.contrib.auth.backends.ModelBackend')
                return redirect('movies:index')
        else:
            form = CustomUserCreationForm()
        context = {'form': form}
        return render(request,'accounts/signup.html',context)

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, '이미 로그인이 된 상태입니다. 즐겁게 이용해주세요 😊')
        return redirect('movies:index')
    else:
        if request.method == 'POST':
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                auth_login(request,form.get_user())
                return redirect('movies:index')
        else:
            form = AuthenticationForm()
        context = {'form':form}
        return render(request,'accounts/login.html',context)

def logout(request):
    if request.user.is_anonymous:
        messages.error(request,'로그인을 안 하셨는데 로그아웃이라뇨! 농담두~ 😋')
    else:
        messages.success(request,'로그아웃이 되었습니다! 또 찾아와주세요!')
        auth_logout(request)
    return redirect('movies:index')

def profile(request,user_pk):
    if request.user.pk != user_pk:
        messages.error(request,'남의 프로필을 보진 말아주세요! 👿')
        return redirect('movies:index')
    else:
        user = get_object_or_404(User,pk=user_pk)
        context = {
            'user': user
        }
        return render(request,'accounts/profile.html',context)