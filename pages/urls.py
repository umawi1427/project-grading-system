from django.urls import path
from .views import (
    HomeView,
    LoginView,
    SignupView,
    LogoutView,
    AboutView,
    ContactView,
    ProfileStudentView,
    SubmitProjectView,
    ProfileTeacherView,
    GradeProjectView,
    AdminPageView,
    MyProjectsView,
)
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import PasswordResetConfirmView

urlpatterns = [
    path('', HomeView.render, name='home'),
    path('login/', LoginView.post, name='login'),
    path('signup/', SignupView.post, name='signup'),
    path('logout/', LogoutView.logout, name='logout'),
    path('about/', AboutView.render, name='about'),
    path('contact/', ContactView.render, name='contact'),
    path('profile/student/', ProfileStudentView.render, name='profileStudent'),
    path('submit_project/', SubmitProjectView.submit, name='submit_project'),
    path('profile/teacher/', ProfileTeacherView.render, name='profileTeacher'),
    path('grade_project/<int:project_id>/', GradeProjectView.grade, name='grade_project'),
    path('admin_page/', AdminPageView.render, name='admin_page'),
    path('my_projects/', MyProjectsView.render, name='my_projects'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='pages/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='pages/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='pages/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='pages/password_reset_complete.html'), name='password_reset_complete'),
]

handler404 = 'pages.views.custom_page_not_found_view'
handler500 = 'pages.views.custom_error_view'