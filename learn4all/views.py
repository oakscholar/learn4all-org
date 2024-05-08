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
import openai, os, sys, json, re
from django.views import View
from django.conf import settings
# import boto3
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
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




class DescribeGoalView(LoginRequiredMixin,FormView):
    template_name = 'learning-plan/describe_goal.html'
    form_class = GoalForm
    success_url = reverse_lazy('evaluateLearningStyle')  
    login_url = '/login/'

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return super(DescribeGoalView, self).form_valid(form)
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        goal = data.get('goal')
        if request.user.is_authenticated:
            Profile.objects.update_or_create(
                user=request.user,
                defaults={'goal': goal}
            )
            return JsonResponse({'status': 'success', 'message': 'Goal updated'})
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)


class EvaluateLearningStyleView(LoginRequiredMixin,FormView):
    template_name = 'learning-plan/evaluate_learning_style.html'
    form_class = LearningStyleForm
    success_url = reverse_lazy('resultLearningStyle')  
    login_url = '/login/'

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return super(DescribeGoalView, self).form_valid(form)
    

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        learning_style = data.get('learning_style')
        user = request.user

        if user.is_authenticated:
            profile, created = Profile.objects.update_or_create(
                user=user,
                defaults={'learning_style': learning_style}
            )
            return JsonResponse({'status': 'success', 'message': 'Profile updated', 'user_id': user.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

    
def get_user_profile(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    return profile


def create_prompt(profile): #Provide valid JSON output. 
    prompt = (f"Provide valid JSON output. Generate a detailed 5-week study plan in JSON format, tailored for an individual with specific attributes. "
            f"Profile details: Goal - {profile.goal}, Skills - {profile.skill}, Learning Style - {profile.learning_style}. "
            f"Each week should clearly define its learning objectives. "
            f"Provide a comprehensive daily learning plan from Monday to Sunday, listing the activities and specific resources needed each day. "
            f"The output should be structured as JSON to ensure easy integration and practical application in line with the user's goal, skills, and preferred learning style.")
    return prompt



# client = boto3.client('secretsmanager')
# def get_secret():
#     try:
#         get_secret_value_response = client.get_secret_value(
#             SecretId='your_secret_id_or_name_here'
#         )
#     except Exception as e:
#         print("Error retrieving secret: ", e)
#         return None
#     else:
#         secret = get_secret_value_response['SecretString']
#         return json.loads(secret)['OPENAI_API_KEY']

def get_study_plan(prompt):
    openai_api_key = settings.OPENAI_API_KEY 
    # openai.api_key = get_secret()

    if not openai_api_key:
        return None, "Error: The OPENAI_API_KEY environment variable is not set."

    # GPT guidance: https://cookbook.openai.com/examples/how_to_format_inputs_to_chatgpt_models
    # POSTMAN guidance: https://www.postman.com/devrel/workspace/openai/documentation/13183464-90abb798-cb85-43cb-ba3a-ae7941e968da 
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",  # Change the model as per availability or requirements; gpt-3.5-turbo-instruct;gpt-3.5-turbo, gpt-4, gpt-3.5-turbo-16k-1106
        prompt=prompt,
        max_tokens=3500,  
    )
    return response.choices[0].text


class GenerateStudyPlanView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if request.user.id != int(user_id):
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        if request.user.id != user_id:
            # Return a forbidden response if the user does not match
            return HttpResponseForbidden("You are not authorized to view this page.")

        if request.user.is_authenticated and request.user.id == user_id:
            profile = get_object_or_404(Profile, user_id=user_id)
            prompt = create_prompt(profile)
            study_plan = get_study_plan(prompt)
            # context = {"study_plan":study_plan}
            context = json.loads(study_plan)#parse_study_plan(context)
            print('test-context',context)
            context.update({
                'user_id': user_id,  # Pass user_id to use in the JavaScript fetch call
                'first_name': request.user.first_name  
            })
            
            return render(request, 'learning-plan/result_learning_style.html',context)