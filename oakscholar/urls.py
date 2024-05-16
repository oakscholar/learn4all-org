"""
URL configuration for oakscholar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth.views import LogoutView
from learn4all.views import *
from learn4all import views
from django.contrib.auth.views import LogoutView 
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),


    # Navigation Bar
    path('', views.home, name='home'),
    path('about/', views.home, name='about'),
    path('plan/', views.home, name='plan'),
    path('contact/', views.home, name='contact'),
    path("login/", MyLoginView.as_view(template_name='profile/login.html'), name="login"),
    path("signup/", SignUpView.as_view(template_name='profile/signup.html'), name="signup"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('profile/', views.update_profile, name='profile'),


    # Features
    path('schedule-interview/', views.schedule_interview, name='schedule'),

    # Learning Plan 
    path('describe_goal/', views.DescribeGoalView.as_view(), name='describeGoal'),
    path('evaluate_learning_style/', views.EvaluateLearningStyleView.as_view(), name='evaluateLearningStyle'),
    path('result_learning_style/<int:user_id>/', views.GenerateStudyPlanView.as_view(), name='resultLearningStyle'),
    re_path(r'^result_learning_style/(.*)$', TemplateView.as_view(template_name='index.html')),
    
    path('loading_page/', views.LoadingPageView.as_view(), name='loadingPage'),

    
]
