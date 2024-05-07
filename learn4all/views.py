from django.shortcuts import get_object_or_404, render,redirect
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
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
import openai, os
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
# User = get_user_model()
# user = User.objects.get(username='user02')
# print(user.get_all_permissions())

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "profile/signup.html"
    success_url = reverse_lazy("describeGoal")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        response = super().form_valid(form)
        # Authenticate user then login
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')  # the raw password
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        return response

class MyLoginView(LoginView):
    template_name = "profile/login.html"
    redirect_authenticated_user = True
    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy("admin:index") # Changed if needed
        else:
            # return reverse_lazy("home") # TO-DO: Change to profile
            return reverse_lazy("describeGoal")

def home(request):
    return render(request, 'home/home.html')

def schedule_interview(request):
    # TO-DO: DB logic inside
    return render(request, 'schedule_interview.html')

def update_profile(request):
    # TO-DO: both logic and html
    return render(request, 'profile_update.html')




class DescribeGoalView(FormView):
    template_name = 'learning-plan/describe_goal.html'
    form_class = GoalForm
    success_url = reverse_lazy('evaluateLearningStyle')  
    login_url = '/login/'

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return super(DescribeGoalView, self).form_valid(form)
    

class EvaluateLearningStyleView(FormView):
    template_name = 'learning-plan/evaluate_learning_style.html'
    form_class = LearningStyleForm
    success_url = reverse_lazy('resultLearningStyle')  
    login_url = '/login/'

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return super(DescribeGoalView, self).form_valid(form)

    
def get_user_profile(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    return profile


def create_prompt(profile):
    prompt = (f"Create a personalized 10-week study plan for a user with the following details: "
              f"Goal: {profile.goal}, Skills: {profile.skill}, Learning Style: {profile.learning_style}."
              f"I need weekly learning objectives and a detailed daily learning plan, such as what specific resources I need to learn each day")
    return prompt


def get_study_plan(prompt):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # GPT guidance: https://cookbook.openai.com/examples/how_to_format_inputs_to_chatgpt_models
    # POSTMAN guidance: https://www.postman.com/devrel/workspace/openai/documentation/13183464-90abb798-cb85-43cb-ba3a-ae7941e968da 
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",  # Change the model as per availability or requirements; gpt-3.5-turbo, gpt-4, gpt-3.5-turbo-16k-1106
        prompt=prompt,
        # max_tokens=1500,  
    )
    return response.choices[0].text


@method_decorator(login_required, name='dispatch')
def GenerateStudyPlanView(request, user_id): # result_learning_style.html
    if not request.user.is_authenticated: 
        return HttpResponse("You are not authorized to view this page.", status=401)
    
    def get(self, request):
        user_id = request.user.id 
        profile = get_user_profile(request, user_id)
        prompt = create_prompt(profile)
        study_plan = get_study_plan(prompt)
        return HttpResponse(study_plan)
