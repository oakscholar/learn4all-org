from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views.generic.list import ListView
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from learn4all.forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from .forms import *
from django.http import HttpResponse
from django.shortcuts import render
from .models import Profile

# Create your views here.
# User = get_user_model()
# user = User.objects.get(username='user02')
# print(user.get_all_permissions())

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "profile/signup.html"
    success_url = reverse_lazy("login")


class MyLoginView(LoginView):
    template_name = "profile/login.html"
    redirect_authenticated_user = True
    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy("admin:index") # Changed if needed
        else:
            return reverse_lazy("home")

def home(request):
    return render(request, 'home/home.html')

def schedule_interview(request):
    # TO-DO: DB logic inside
    return render(request, 'schedule_interview.html')

def update_profile(request):
    # TO-DO: both logic and html
    return render(request, 'profile_update.html')


