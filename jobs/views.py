from django.shortcuts import render, redirect
from .models import Profile , Jobs, Application
from django.template import loader
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, JobForm, RegistrationForm, ApplicationForm, ProfileForm
from django.contrib.auth import authenticate as auth, login as auth_login, logout as auth_logout
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib import messages


def home(request):
    return render(request, "jobs/home.html")

def signup(request):
    if request.method=="POST":
        form= RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user= form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form=RegistrationForm()
    return render(request, "jobs/signup.html", {'form':form})

def login_view(request):
    if request.method=="POST":
        form= LoginForm(request, data=request.POST)
        if form.is_valid():
            user= form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form=LoginForm()
    return render(request, "jobs/login.html", {'form': form})


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')

@login_required
def job_create(request):
    if request.user.profile.role != "employer":
        messages.error(request, "Only employers can post jobs.")
        return redirect("home")
    
    if request.method=="POST":
        form= JobForm(request.POST)
        if form.is_valid():
            #not form.instance.user=request.user but the next line is the correct way to do that in this situation
            form.instance.profile = request.user.profile
            form.save()
            return redirect('job_list')
    else:
        form= JobForm()
    return render(request, "jobs/job_form.html" , {'form':form})


def job_list(request):
    jobs= Jobs.objects.all().order_by("-id")
    return render(request, "jobs/job_list.html", {'jobs':jobs})


def job_detail(request, job_id):
    job= get_object_or_404(Jobs, id=job_id)
    return render(request, "jobs/job_detail.html", {"job":job})

@login_required
def application_create(request, app_id):
    job= get_object_or_404(Jobs, id=app_id)
    if request.user.profile == job.profile:
        messages.warning(request, "You cannot apply to the job you have posted")
        return redirect('job_detail', job_id=app_id)
    if request.method=="POST":
        form= ApplicationForm(request.POST, request.FILES)#the request.FILES is for cv upload
        if form.is_valid():
            if Application.objects.filter(profile=request.user.profile).exists():
                #the above condition help handling duplication
                #it check if a user already submitted an application to a job ,
                #to avoid double application
                # Handle duplicate (e.g., redirect with message)
                messages.warning(request, "You've already applied for this job.")
                return redirect('job_detail', job_id=app_id)
            else:
                application= form.save(commit=False) #Prevents premature save with null fields.can cause a issue sometime if there not "commit=False"
                application.profile= request.user.profile
                application.job= job
                application.save()
                
                return redirect('job_list')
    #what the above code does is:
    #Saves the application: Associates with user's profile and the specific job.
    else:
        form= ApplicationForm()
    return render(request, "jobs/application_form.html", {'form':form, 'job':job})

@login_required
def application_detail(request, app_id):
    app = get_object_or_404(Application, id=app_id, job__profile=request.user.profile)

    if request.method == "POST":
        action = request.POST.get("action")
        if action in ["reviewed", "accepted", "rejected"]:
            app.status = action
            app.save()
            messages.success(request, f"Application marked {action}.")
            return redirect("employer_applicants")

    return render(request, "jobs/application_detail.html", {"application": app})

@login_required
def application_update(request, app_id):
    application = get_object_or_404(Application, id=app_id, profile=request.user.profile)
    
    # Prevent editing if status is not 'applied', necessary for all the kinds of things tht will need application or any other kind of form 
    if application.status != 'applied':
        messages.error(request, "You can only edit applications that are still pending.")
        return redirect('profile_detail', profile_id=request.user.profile.id)
    
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated successfully!")
            return redirect('profile_detail', profile_id=request.user.profile.id)
    else:
        form = ApplicationForm(instance=application)
    
    return render(request, "jobs/application_form.html", {'form': form, 'job': application.job, 'is_update': True})

@login_required
def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Handle profile editing if it's the user's own profile, avoid user to edit the profile of another user
    is_own_profile = (profile == request.user.profile)
    profile_form = None
    if is_own_profile:
        if request.method == "POST" and 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile_detail', profile_id=profile.id)
        else:
            profile_form = ProfileForm(instance=profile)
    
    if profile.role == "employer":
        jobs = profile.jobs.all().order_by('-created_at')
        context = {'profile': profile, 'jobs': jobs, 'is_own_profile': is_own_profile, 'profile_form': profile_form}
    else:
        applications = Application.objects.filter(profile=profile).select_related('job').order_by('-applied_at')
        context = {'profile': profile, 'applications': applications, 'is_own_profile': is_own_profile, 'profile_form': profile_form}
    return render(request, "jobs/profile_detail.html", context)

def job_delete(request, job_id):
    job= get_object_or_404(Jobs, id=job_id)
    if request.method== "POST":
        job.delete()
        return  redirect('job_list')
    return render(request , "jobs/job_confirm_delete.html", {'job':job})

@login_required
def job_update(request, job_id):
#    job= get_object_or_404(Jobs, id=job_id)
#    if request.method=="POST":
#        form= JobForm(request.POST)  #here instance=job is needed ,
#        #otherwise instead of updating , the Form will be creating a new form 
#        form.save()
#        return redirect('jobs_list') #here i was redirecting to the view reason why ,it was not working 

    job = get_object_or_404(Jobs, id=job_id)
    
    # Prevent non-owners from editing , necessary when you have multiple role on your app, like in this project ,i have "employer" and "candidate" 

    if request.user.profile != job.profile:
        messages.error(request, "You don't have permission to edit this job.")
        return redirect('job_detail', job_id=job.id)
    
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
        #also "instance=job" is needed here to return the job data on GET method after the update before rendering the specified timeframe
    
    return render(request, "jobs/job_form.html", {'form': form, 'job': job})

    

#def job_delete(request, job_id):
#    pass

@login_required
def employer_applicants(request):
    profile = request.user.profile
    if profile.role != "employer":
        messages.error(request, "Only employers can access this page.")
        return redirect("home")

    apps = Application.objects.filter(job__profile=profile).select_related("job", "profile__user")

    return render(request, "jobs/employer_applicants.html", {"applications": apps})

