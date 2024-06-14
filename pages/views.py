import logging
import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Profile, NewClassName
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
from .forms import CustomSetPasswordForm
from django.shortcuts import render, get_object_or_404, redirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.template import Context
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import letter

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
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            teacher_id = request.POST.get('teacher')
            file = request.FILES.get('file')

            errors = []
            if not title:
                errors.append('Title is required.')
            if not description:
                errors.append('Description is required.')
            if not teacher_id:
                errors.append('Teacher is required.')
            if not file:
                errors.append('File is required.')
            try:
                teacher = User.objects.get(id=teacher_id)
                if not teacher.profile.major == 'teacher':
                    errors.append('Selected user is not a teacher.')
            except User.DoesNotExist:
                errors.append('Teacher does not exist.')

            if errors:
                current_user = request.user
                teachers = User.objects.filter(profile__major='teacher')
                return render(request, 'pages/profileStudent.html', {'user': current_user, 'errors': errors, 'teachers': teachers})
            
            project = NewClassName(
                title=title,
                description=description,
                teacher=teacher,
                file=file,
                student=request.user
            )
            project.save()
            return redirect('my_projects')

        current_user = request.user
        teachers = User.objects.filter(profile__major='teacher')
        return render(request, 'pages/profileStudent.html', {'user': current_user, 'teachers': teachers})

@login_required(login_url='login')
def my_projects(request):
    current_user = request.user
    projects = NewClassName.objects.filter(student=current_user)
    return render(request, 'pages/my_projects.html', {'user': current_user, 'projects': projects})


def download_project_description(request, project_id):
    try:
        project = NewClassName.objects.get(id=project_id)
    except NewClassName.DoesNotExist:
        return HttpResponse("Project not found.", status=404)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{project.title}_description.pdf"'
    try:
        p = canvas.Canvas(response, pagesize=letter)
        background_image_path = os.path.join(os.getcwd(), 'media', '1.png')
        width, height = letter        
        p.setFillColor(colors.white)
        p.rect(0, 0, width, height, fill=True)        
        image_width = 150
        image_height = 150
        image_x = (width - image_width) / 2
        image_y = (height - image_height) / 2        
        p.drawImage(background_image_path, image_x, image_y, width=image_width, height=image_height, mask='auto', preserveAspectRatio=True)       
        title_text = f"Project Title: {project.title}"
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.blue)
        p.drawString(100, height - 50, title_text)        
        student_name_text = f"Student Name: {project.student.get_full_name()}"
        p.setFont("Helvetica", 12)
        p.setFillColor(colors.black)
        p.drawString(100, height - 80, student_name_text)        
        description_text = f"Description:\n{project.description}"
        p.setFont("Helvetica", 12)
        p.setFillColor(colors.black)
        y_position = height - 120
        lines = description_text.splitlines()
        for line in lines:
            p.drawString(100, y_position, line)
            y_position -= 20  
        p.showPage()
        p.save()
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
    return response

logger = logging.getLogger(__name__)

class ProfileTeacherView:
    @staticmethod
    @login_required(login_url='login')
    def render(request):
        projects = NewClassName.objects.filter(teacher=request.user)
        return render(request, 'pages/profileTeacher.html', {'projects': projects})

    @staticmethod
    @login_required(login_url='login')
    def grade_project(request, project_id):
        if request.method == 'POST':
            grade = request.POST.get('grade')
            project = get_object_or_404(NewClassName, id=project_id)
            if project.teacher == request.user:
                project.grade = grade
                project.save()
            else:
                messages.error(request, "You are not authorized to grade this project.")

        logger.debug(f"File URL: {project.file.url}")  
        return redirect('profileTeacher')
    
def download_file(request, file_path):
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    if os.path.exists(full_file_path):
        with open(full_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return HttpResponse("File not found", status=404)

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