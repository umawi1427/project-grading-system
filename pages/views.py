from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Profile, Project
from django.core.mail import send_mail
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.views import PasswordResetConfirmView
from .forms import CustomSetPasswordForm, ProjectForm, GradeForm
from django.shortcuts import render, get_object_or_404, redirect

def custom_error_view(request):
    return render(request, '500.html', status=500)

def custom_page_not_found_view(request, exception):
    return HttpResponseNotFound('')

class HomeView:
    @staticmethod
    def render(request):
        return render(request, 'pages/home.html')

class LoginView:
    @staticmethod
    def post(request):
        current_user = request.user
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user_list = User.objects.all()
            guest = True
            for user in user_list:
                if str(user) == str(username):
                    guest = False
                    break
            if not guest:
                useru = User.objects.get(username=username)
                if useru.check_password(password):
                    user = authenticate(request, username=username, password=password)
                    try:
                        profile = Profile.objects.get(user=user)
                    except Profile.DoesNotExist:
                        messages.error(request, f"No profile found for user {user.username}", extra_tags='error')
                    if profile.is_approved:
                        auth_login(request, user)
                        if username == 'PGS' and password == 'PGS-2024':
                            return redirect('admin_page')
                        elif profile.major == 'student':
                            return redirect('profileStudent')
                        elif profile.major == 'teacher':
                            return redirect('profileTeacher')
                        elif profile.major == 'superuser':
                            return redirect('http://127.0.0.1:8000/admin')
                        else:
                            return render(request, 'pages/home.html',
                                          {'user': current_user, 'guest': False, 'notmatch': False,
                                           'logged': True})
                    else:
                        messages.error(request, 'Your account has not been approved yet')
                        return render(request, 'pages/login.html',
                                      {'guest': False, 'notmatch': False, 'logged': False})
                else:
                    return render(request, 'pages/login.html', {'guest': False, 'notmatch': True})
            else:
                return render(request, 'pages/login.html', {'guest': True, 'notmatch': False})
        else:
            if request.user.is_authenticated:
                try:
                    profile = Profile.objects.get(user=request.user)
                    if profile.major == 'student':
                        return redirect('profileStudent')
                    elif profile.major == 'teacher':
                        return redirect('profileTeacher')
                    elif profile.major == 'superuser':
                        return redirect('http://127.0.0.1:8000/admin')
                    else:
                        return redirect('home')
                except Profile.DoesNotExist:
                    messages.error(request, f"No profile found for user {request.user.username}",
                                   extra_tags='error')
                    return redirect('home')
            else:
                return render(request, 'pages/login.html', {'user': request.user})

class SignupView:
    @staticmethod
    def post(request):
        form_data = {}
        errors = []
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password1']
            name = request.POST['name']
            sex = request.POST['sex']
            major = request.POST['option']
            form_data = {'username': username, 'email': email, 'name': name, 'sex': sex, 'major': major}
            if ' ' not in name:
                errors.append('Please enter your last name')
            if User.objects.filter(username=username).exists():
                errors.append('Username already exists.')
            if User.objects.filter(email=email).exists():
                errors.append('Email already exists.')
            if errors:
                return render(request, 'pages/signup.html', {'errors': errors, 'form_data': form_data})
            else:
                first_name, last_name = name.split()
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
                user.save()
                profile = Profile.objects.create(user=user, sex=sex, major=major, is_approved=False)
                profile.save()
                if username == 'PGS' and password == 'PGS-2024':
                    admin = User.objects.get(username='PGS')
                    if not Profile.objects.filter(user=admin).exists():
                        Profile.objects.create(user=admin, sex='N/A', major='N/A', is_approved=True)
                    admin_profile = Profile.objects.get(user=admin)
                    admin_profile.requests.add(profile)
                messages.success(request,'Your account has been created successfully. It is currently pending admin approval. Please keep an eye on your email, as you will receive a notification regarding the approval status')
                return redirect('login')
        else:
            return render(request, 'pages/signup.html', {'form_data': form_data})

class IsAdmin:
    @staticmethod
    def check(user):
        return user.username == 'PGS'

class LogoutView:
    @staticmethod
    @login_required(login_url='login')
    def logout(request):
        auth_logout(request)
        return redirect('home')

class AboutView:
    @staticmethod
    def render(request):
        return render(request, 'pages/about.html')

class ContactView:
    @staticmethod
    def render(request):
        return render(request, 'pages/contact.html')

class ProfileStudentView:
    @staticmethod
    @login_required(login_url='login')
    def render(request):
        current_user = request.user
        form = ProjectForm()
        context = {'form': form, 'user': current_user}
        return render(request, 'pages/profileStudent.html', context)

class SubmitProjectView:
    @staticmethod
    @login_required(login_url='login')
    def submit(request):
        if request.method == 'POST':
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                project = form.save(commit=False)
                project.student = request.user.profile
                project.save()
                return redirect('profileStudent')
        else:
            form = ProjectForm()
        return render(request, 'pages/profileStudent.html', {'form': form})

class ProfileTeacherView:
    @staticmethod
    @login_required(login_url='login')
    def render(request):
        current_user = request.user
        projects_to_grade = Project.objects.filter(teacher=current_user)
        return render(request, 'pages/profileTeacher.html', {'user': current_user, 'projects': projects_to_grade})

class GradeProjectView:
    @staticmethod
    @login_required(login_url='login')
    def grade(request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if request.method == 'POST':
            form = GradeForm(request.POST, instance=project)
            if form.is_valid():
                form.save()
                return redirect('profileTeacher')
        else:
            form = GradeForm(instance=project)
        return render(request, 'pages/profileTeacher.html', {'form': form, 'project': project})

class AdminPageView:
    @staticmethod
    @login_required(login_url='login')
    @user_passes_test(IsAdmin.check)
    def render(request):
        profiles = Profile.objects.all()
        if request.method == 'POST':
            profile_id = request.POST['profile_id']
            new_major = request.POST['major']
            is_approved = request.POST.get('is_approved', False) == 'on'
            action = request.POST['action']
            profile = Profile.objects.get(id=profile_id)
            if action == 'Update Major':
                profile.major = new_major
                profile.is_approved = is_approved
                profile.save()
                if is_approved:
                    send_mail(
                        'Your profile has been approved',
                        'Congratulations, your profile has been approved by the admin. ' + new_major + ' is now your major. You can now login to the system and start using it.',
                        'projectgradingsystem@gmail.com',
                        [profile.user.email],
                        fail_silently=False,
                    )
            elif action == 'Delete User':
                user = profile.user
                user.delete()
        return render(request, 'pages/admin_page.html', {'profiles': profiles})

class MyProjectsView:
    @staticmethod
    @login_required(login_url='login')
    def render(request):
        projects = Project.objects.filter(student=request.user.profile)
        return render(request, 'pages/my_projects.html', {'projects': projects})