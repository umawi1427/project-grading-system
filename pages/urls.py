from django.urls import path
from .views import (
    HomeView,
    LoginView,
    SignupView,
    LogoutView,
    AboutView,
    ContactView,
    ProfileStudentView,
    ProfileTeacherView,
    AdminPageView,
    my_projects,
)
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import PasswordResetConfirmView
from pages import views

urlpatterns = [
    path('', HomeView.render, name='home'),
    path('login/', LoginView.post, name='login'),
    path('signup/', SignupView.post, name='signup'),
    path('logout/', LogoutView.logout, name='logout'),
    path('about/', AboutView.render, name='about'),
    path('contact/', ContactView.render, name='contact'),
    path('profile/student/', ProfileStudentView.render, name='profileStudent'),
    path('my_projects/', my_projects, name='my_projects'),
    path('download-description/<int:project_id>/', views.download_project_description, name='download_description'),
    path('profile/teacher/', ProfileTeacherView.render, name='profileTeacher'),
    path('profile/teacher/grade/<int:project_id>/', ProfileTeacherView.grade_project, name='grade_project'),
    path('download/<str:file_path>/', views.download_file, name='download_file'),
    path('admin_page/', AdminPageView.render, name='admin_page'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='pages/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='pages/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='pages/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='pages/password_reset_complete.html'), name='password_reset_complete'),
]
handler404 = 'pages.views.custom_page_not_found_view'
handler500 = 'pages.views.custom_error_view'