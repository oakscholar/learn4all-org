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
from django.views.generic import TemplateView
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
            return reverse_lazy("admin:index")
        else:
            return reverse_lazy("describeGoal")

    def post(self, request, *args, **kwargs):
        login_failed = False
        email_form = EmailLoginForm(request.POST)
        username_form = UsernameLoginForm(data=request.POST)

        if 'email' in request.POST:
            print("Email form submitted")
            if email_form.is_valid():
                email = email_form.cleaned_data['email']
                password = email_form.cleaned_data['password']
                print(f"Email: {email}, Password: {password}")
                user = authenticate(request, email=email, password=password)
                print(f"Authenticated user: {user}")
                if user is not None:
                    login(request, user)
                    return redirect(self.get_success_url()) 
                else:
                    login_failed = True
                    email_form.add_error(None, "Invalid email or password")
                    print("Invalid email or password")
            else:
                print("Email form is invalid")
                print(email_form.errors)
        else:
            print("Username form submitted")
            if username_form.is_valid():
                user = username_form.get_user() 
                login(request, user)
                return self.form_valid(username_form, user)
            else:
                login_failed = True
                username_form.add_error(None, "Invalid username or password")
                print("Invalid username or password")
                print(username_form.errors)

        return render(request, 'profile/login.html', {
                    'email_form': email_form,
                    'username_form': username_form,
                    'login_failed': login_failed,
                })
    
    def form_valid(self, form, user):
        login(self.request, form.get_user())
        return redirect(self.get_success_url())  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_form'] = EmailLoginForm()
        context['username_form'] = UsernameLoginForm()
        return context
    

def home(request):
    return render(request, 'home/home.html')


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

  
class TimeCommitmentView(LoginRequiredMixin, FormView):
    template_name = 'learning-plan/choose_time_commitment.html'
    form_class = TimeCommitmentForm
    success_url = reverse_lazy('loadingPage')
    login_url = '/login/'

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        learning_wks = data.get('learning_wks')
        learning_hrs_per_wk = data.get('learning_hrs_per_wk')
        user = request.user

        if user.is_authenticated:
            profile, created = Profile.objects.update_or_create(
                user=user,
                defaults={'learning_wks': learning_wks, 'learning_hrs_per_wk': learning_hrs_per_wk}
            )
            print("1", learning_hrs_per_wk,learning_wks)
            return JsonResponse({'status': 'success', 'message': 'Profile updated', 'user_id': user.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
        


def get_user_profile(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    return profile


# Loading_page
class LoadingPageView(LoginRequiredMixin,TemplateView):
    template_name = 'learning-plan/loading_page.html'
    success_url = reverse_lazy('resultLearningStyle')  
    login_url = '/login/'

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return super(LoadingPageView, self).form_valid(form)
    
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.id
        return context


def create_prompt(profile): #Provide valid JSON output. 
    # prompt = (f"Provide valid JSON output. Generate a detailed 5-week study plan in JSON format, tailored for an individual with specific attributes. "
    #         f"Profile details: Goal - {profile.goal}, Skills - {profile.skill}, Learning Style - {profile.learning_style}. "
    #         f"Each week should clearly define its learning objectives. "
    #         f"Provide a comprehensive daily learning plan from Monday to Sunday, listing the activities and specific resources needed each day. "
    #         f"The output should be structured as JSON to ensure easy integration and practical application in line with the user's goal, skills, and preferred learning style.")
    prompt = (f"Create a {profile.learning_wks}-week study plan in JSON format, specifically tailored to a user's profile with detailed attributes. "
              f"User can study for {profile.learning_hrs_per_wk} hours per week, but only give me the general wk plans for now."
              f"The profile details are as follows: Goal - {profile.goal}, Skills - {profile.skill}, Learning Style - {profile.learning_style}. "
              f"Format the output as a JSON object with a top-level key '{profile.learning_wks}-week_study_plan' containing an array of week objects. "
              f"Each week object should include the following keys: "
              f"'week_number' with a value from 1 to {profile.learning_wks}, "
              f"'learning_objectives' as an array of strings describing the goals for the week, "
              f"Ensure that each week is comprehensive and tailored to progressively achieve the user's goal, build on skills, and align with the preferred learning style. "
              f"Here is an example structure for clarity:\n"
              f"{{\n"
              f"  '{profile.learning_wks}-week_study_plan': [\n"
              f"    {{\n"
              f"      'week_number': 1,\n"
              f"      'learning_objectives': ['objective1', 'objective2'],\n"
              f"    }}\n"
              f"    // continue with other weeks\n"
              f"  ]\n"
              f"}}\n"
              f"This detailed prompt should guide you to generate a consistent and structured output suitable for integration into an educational platform.")

            #   f"and keys for each day of the week ('monday' to 'sunday'). "
            #   f"Each day key should map to an object with 'activities' as an array of strings detailing planned study activities, "
            #   f"and 'resources' as an array of strings listing the necessary materials. "
            #   f"Ensure that each week is comprehensive and tailored to progressively achieve the user's goal, build on skills, and align with the preferred learning style. "
            #   f"Here is an example structure for clarity:\n"
            #   f"{{\n"
            #   f"  '5-week_study_plan': [\n"
            #   f"    {{\n"
            #   f"      'week_number': 1,\n"
            #   f"      'learning_objectives': ['objective1', 'objective2'],\n"
            #   f"      'monday': {{ 'activities': ['activity1', 'activity2'], 'resources': ['resource1', 'resource2'] }},\n"
            #   f"      // continue with other days\n"
            #   f"    }}\n"
            #   f"    // continue with other weeks\n"
            #   f"  ]\n"
            #   f"}}\n"
            #   f"This detailed prompt should guide you to generate a consistent and structured output suitable for integration into an educational platform."
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
            return HttpResponseForbidden("You are not authorized to view this page.")
        
        if request.user.is_authenticated and request.user.id == user_id:
            learning_result = check_learning_result(request)
            print("learning_result from db:", learning_result)
            if learning_result:
                return render(request, 'learning-plan/result_learning_style.html', {'json_context': json.dumps(learning_result)})
        
            profile = get_object_or_404(Profile, user_id=user_id)
            prompt = create_prompt(profile)
            study_plan = get_study_plan(prompt)
            print("gpt:", study_plan)
            context = json.loads(study_plan) # parse_study_plan(context)
            print('test-context', context)
            json_context = json.dumps(context)

            # Ensure general_wk_result is set correctly when the LearningResult object is created
            learning_result, created = LearningResult.objects.get_or_create(profile=profile, defaults={'general_wk_result': context})

            if not created:
                learning_result.general_wk_result = context
                learning_result.save()

            return render(request, 'learning-plan/result_learning_style.html', {'json_context': json_context})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = int(self.kwargs['user_id'])
        return context


@login_required
def get_learning_weeks(request):
    profile = Profile.objects.get(user=request.user)
    return JsonResponse({'learning_wks': profile.learning_wks})


@login_required
def check_learning_result(request):
    try:
        learning_result = LearningResult.objects.get(profile__user=request.user)
        if learning_result.general_wk_result:
            return learning_result.general_wk_result
        else:
            return None
    except LearningResult.DoesNotExist:
        return None