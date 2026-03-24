from . import views
from django.urls import path

urlpatterns=[
    path('', views.home, name="home"),
    #the name in int:job_id,  i mean "job_id" need to match the one used  
    #as a parameter in the view function job_detail(request, job_id)
    #if the two name don't match it won't work , there'll a issue in the browser
    path('job_detail/<int:job_id>', views.job_detail, name="job_detail"),
    path('job_list/', views.job_list, name="job_list"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('job_create/', views.job_create, name="job_create"),
    #path('application_form/', views.application_form, name="application_form"),
    path('profile_detail/<int:profile_id>', views.profile_detail, name="profile_detail"),
    path('job_confirm_delete/', views.job_delete, name="job_confirm_delete"),
    path('login/', views.login_view, name="login_view"),
    path('application_create/<int:app_id>', views.application_create, name="application_create"),
    path('application_update/<int:app_id>', views.application_update, name="application_update"),
    path('job_update/<int:job_id>', views.job_update, name="job_update"),
    path('job_delete/<int:job_id>', views.job_delete, name="job_delete"),
    path('employer/applicants/', views.employer_applicants, name='employer_applicants'),
    path('employer/application/<int:app_id>/', views.application_detail, name='application_detail'),
    path("employer/applicants/", views.employer_applicants, name="employer_applicants"),
    path("employer/application/<int:app_id>/", views.application_detail, name="application_detail"),
]