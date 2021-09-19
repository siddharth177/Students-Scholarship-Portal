from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from content.decorators import login_required_message
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import datetime
from accounts.models import Department
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def checkuserifscrutinyuser(user):
    if user.groups.filter(name="owner").exists() and user.is_superuser:
        return True
    else:
        return False

def is_user_eligible(user, sch):
    print(sch.caste, user.caste)
    if(sch.caste != 'NA' and sch.caste != user.caste):
        return False
    print(sch.program, user.program)
    if(sch.program != 'NA' and sch.program != user.program):
        return False
    print(sch.specialization, user.specialization           )
    if(sch.specialization != 'NA' and sch.specialization != user.specialization):
        return False
    print(sch.gender, user.gender)
    if(sch.gender != 'NA'and sch.gender != user.gender):
        return False
    # if(sch.minimum_cgpa != 'NA' && sch.minimum_cgpa != user.minimum_cgpa):
    #     return false
    return True


@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Show_Scholarships(request):
    response = {}
    user = CustomUser.objects.get(pk = request.user.id)
    all_scholarships = Scholarship.objects.all()
    eligible = []
    for sch in all_scholarships:
        if is_user_eligible(user, sch):
            eligible.append(True)
        else:
            eligible.append(False)
            print("ELSE", eligible[-1])
    response['scholarships'] = zip(all_scholarships, eligible)
    return render(request, 'content/all_scholarships.html', response)

@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Scholarship_Detail(request, s_id):
    response = {}
    app = Application.objects.filter(request=s_id, applicant=request.user.id)
    if len(app)>0:
        response['alreadyApplied'] = True
        response['app_id'] = app[0].app_id
        print("IF : ",response['app_id'])
    else:
        response['alreadyApplied'] = False
        response['app_id'] = None
        print("ELSE : ", response['app_id'])

    response['scholarship'] = Scholarship.objects.get(pk=s_id)

    return render(request, 'content/scholarship_detail.html', response)

@csrf_exempt
@login_required(login_url="/login/")
def Apply(request):
    print("APPLIED")
    s_id = request.POST.get('scholarship_id')
    sch = get_object_or_404(Scholarship, id = s_id)
    user_id = request.user.id
    user = get_object_or_404(CustomUser,id=user_id)
    app = Application.objects.filter(request=s_id, applicant=user_id)
    if len(app)>0:
        messages.info(request, "You have already applied to this scholarship")
        new_app = app[0]
    else:
        cnt = Application_Count.objects.get()
        year = datetime.datetime.now().year
        yy = str(year)
        p1 = yy[2:]
        p2 = str(cnt.app_cnt).zfill(4)
        Name = "APP"
        app_id = Name + p1 + p2
        cnt.app_cnt += 1
        cnt.save()
        print(app_id)
        new_app = Application.objects.create(app_id=app_id)
        new_app.department = user.department
        new_app.category = request.POST.get('application_type')
        new_app.applicant = user
        new_app.request = sch
        new_app.title = sch.name
        new_app.is_approved = False
        new_app.attached_pdf = request.FILES.get("up_files", False)
        new_app.department_id = user.department
        new_app.save()
        messages.success(request, "You have successfully applied to this scholarship")

    data = {}
    data['alreadyApplied'] = True
    data['scholarship'] = sch
    response = {}
    response['scholarship'] = sch
    response['app_id'] = new_app.app_id
    return render(request, 'content/scholarship_detail.html', response)

@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Show_Pending_Approvals(request):
    applications = Application.objects.all()
    departments = Department.objects.all()
    response = {}
    response['applications'] = applications
    response['departments'] = departments
    return render(request, 'content/show_pending_approvals.html', response)


# @csrf_exempt
# @login_required_message(message="You should be logged in, in order to perform this")
# @login_required(login_url="/login/")
# def Show_Pending_Approval_Docs(request, app_id):
#     response = {}
#     app = Application.objects.filter(app_id=app_id)
#     response['app'] = app[0]
#     print(app[0].attached_pdf)
#     return render(request, 'content/show_documents.html', response)

@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Approve(request, app_id):
    print(app_id)
    app = Application.objects.filter(app_id=app_id)
    if app[0]:
        app = app[0]
    else:
        app = Node
        response = {}
        response['applications'] = applications
        response['departments'] = departments
        return render(request, 'content/show_pending_approvals.html', response)

    app.is_approved = True
    app.is_rejected = False
    app.save()

    to_email = app.applicant.email
    subject = 'Application Status Updated.'
    message = 'Your application has been approved successfully.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to_email]
    # send_mail( subject, message, email_from, recipient_list)

    applications = Application.objects.all()
    departments = Department.objects.all()
    response = {}
    response['applications'] = applications
    response['departments'] = departments
    return render(request, 'content/show_pending_approvals.html', response)


@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Reject(request):
    app_id = request.POST.get('id_checker')
    reason = request.POST.get('reason')
    app_id = str(app_id).strip()
    print(app_id)
    app = Application.objects.get(pk=app_id)
    
    app.is_approved = False
    app.is_rejected = True

    to_email = app.applicant.email
    subject = 'Application Status Updated.'
    message = 'Your application status has been rejected.\nDue to following reason : \n ' + str(reason)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to_email]
    # send_mail(subject, message, email_from, recipient_list)

    app.save()
    applications = Application.objects.all()
    departments = Department.objects.all()
    response = {}
    response['applications'] = applications
    response['departments'] = departments
    designations = {'Teacher', 'Faculty Advisor', 'Dean', 'Head of Department', 'Director'}
    response['designations'] = designations
    return render(request, 'content/show_pending_approvals.html', response)


@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Track_Application(request):
    if request.POST:
        app_id = request.POST.get('app_id')
        application = Application.objects.filter(app_id=app_id)
        for a in application:
            print(a.app_id)
        response = {
            'application': application[0],
        }

    else:
        response = {
            'application': None,
        }
    return render(request, 'application/track_application.html', response)

@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Track_Student_Applications(request):
    if request.POST:
        app_id = request.POST.get('app_id')
        application = Application.objects.filter(app_id=app_id)
        for a in application:
            print(a.app_id)
        response = {
            'application': application[0]
        }
    else:
        response = {
            'application': None
        }
    return render(request, 'application/track_application.html', response)

@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def Add_Scholarship(request):
    if request.method == "POST":
        user = CustomUser.objects.get(pk=request.user.id)
        response = {}
        sch = Scholarship.objects.create(name = request.POST['title'], abbreviation= request.POST['abbreviation'])
        try:
            dept = Department.objects.get(name=request.POST['department'])
            sch.department = dept[0]
        except Exception as e:
            sch.department = None
        sch.requirements_info = request.POST['requirements_info']
        sch.caste = request.POST['caste']
        sch.program = request.POST['program']
        sch.specialization = request.POST['specialization']
        sch.gender = request.POST['gender']
        if request.POST['minimum_cgpa'] == 'NA':
            sch.minimum_cgpa = 0
        else:
            sch.minimum_cgpa = int(request.POST['minimum_cgpa'])
        sch.external_link = request.POST['external_link']
        sch.save()
        messages.success(request, "Scholarship has been added successfully.")
    if request.user.is_admin:
        return render(request, 'content/add_scholarship.html')
    else:
        return render(request, 'student_home.html')

@csrf_exempt
@login_required_message(message="You should be logged in, in order to perform this")
@login_required(login_url="/login/")
def applied_scholarships(request):
    response = {}
    user = CustomUser.objects.get(pk = request.user.id)
    user_applications = Application.objects.filter(applicant=user)
    
    response['user_applications'] = user_applications
    return render(request, 'content/all_applied_scholarships.html', response)