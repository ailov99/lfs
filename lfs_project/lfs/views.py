from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from lfs.models import Teacher, Takers, Module, Page, ContentFile
from lfs_admin.models import Administrator, UserRegistrations, AnonHits
from lfs.forms import UserForm, TeacherForm, ModuleForm, ContentForm, PageForm
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from datetime import date
from django.contrib.auth.hashers import *

import mimetypes
import os

# Logg stuff
import logging
logging.basicConfig(filename='wtf.log',level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------- Basic User Navigation --------------------


def user_register(request):
    """ User registration """

    context_dict = {}

    # pass which navbar tab is active
    context_dict['nbar'] = 'register'

    context_dict['user_form'] = UserForm()
    context_dict['teacher_form'] = TeacherForm()
    context_dict['is_admin'] = False

    # check if user is admin
    if request.user.is_authenticated():
        if Administrator.objects.filter(user = request.user).exists():
            context_dict['is_admin'] = True

    if request.method == 'POST':
        form = UserForm(request.POST)
        # Django's default User model

        if form.is_valid():
            try:
                user = User.objects.create_user(form.cleaned_data['username'],
                                                form.cleaned_data['email'],
                                                form.cleaned_data['password'],
                                                first_name=form.cleaned_data['first_name'],
                                                last_name=form.cleaned_data['last_name'])
            except ValueError:
                # user left an invalid/empty field
                # TODO: Add an error message/indicator for users
                return render(request, 'lfs/login/register.html', {})

            # Use default (empty values) for all other Teacher fields
            Teacher.objects.create(user=user)


            for module in Module.objects.filter(compulsory=True):
                Takers.objects.create(user=user, module=module)

            # Record this registration for statistics
            UserRegistrations.objects.get_or_create(time=date.today())[0].inc()

            return HttpResponseRedirect('/lfs/login/')
        else:
            context_dict['errors'] = form.errors
            print form.errors

    return render(request, 'lfs/login/register.html', context_dict)

def user_login(request):
    """ User login """

    context_dict = {}
    context_dict['nbar'] = 'login'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
	        if user.is_active:
	            # this acc is active
	            login(request, user)
	            # TODO: redirect to dashboard once page is finished
	            return HttpResponseRedirect('/lfs/dashboard/')

	        else:
	            # acc inactive
	            return HttpResponse('Inactive acount')

        else:
	        # bad details
	        context_dict['errors'] = 'Please enter valid login details'
	        return render(request, 'lfs/login/login.html', context_dict)

    else:
        # GET -> display dashboard
        # also record anon user
        if not request.user.is_authenticated():
            # Record this anon user for statistics
            AnonHits.objects.get_or_create(time=date.today())[0].inc()
        return render(request, 'lfs/login/login.html', context_dict)


@login_required
def user_logout(request):
    """ User logout """
    logout(request)

    return HttpResponseRedirect('/lfs/login/')


@login_required
def user_dashboard(request):
    """ User dashboard with all selected modules """
    context_dict = {}
    context_dict['is_admin'] = False

    #check if user is logged in
    if request.user.is_authenticated():
        user = request.user
        #check if user is an admin
        if Administrator.objects.filter(user = user).exists():
            context_dict['is_admin'] = True
        
    # pass which navbar tab is active
    context_dict['nbar'] = 'home'

    # get currently logged in user
    user = request.user
    if not user.is_staff:
        teacher = Teacher.objects.filter(user=user)[0]
        context_dict['teacher'] = teacher

    takers_record = Takers.objects.all()
    # teacher's overall progress =
    # (sum of progress in all modules / # modules taken)
    modules_taken_count = takers_record.filter(user=user).count()
    if modules_taken_count != 0:
        context_dict['overall_progress'] = reduce(lambda x,y: x+y, [i.progress for i in takers_record if i.user==user], 0) / modules_taken_count
    else:
        context_dict['overall_progress'] = 0

    # pass all modules taken by user as a dict(module_name : progress)
    context_dict['modules_progress'] = {i.module : i.progress for i in takers_record if i.user==user}
    if context_dict['is_admin']:
        context_dict['modules_progress'] = {i : 0 for i in Module.objects.all()}
        for i in Module.objects.all():
            Takers.objects.get_or_create(user=user, module=i)
        context_dict['overall_progress'] = 0

    # also pass total number of modules available throughout the platform
    context_dict['modules_total'] = Module.objects.all().count()

    # completed modules
    context_dict['modules_completed'] = {i.module : i.progress for i in takers_record if i.user==user and i.progress == 100}

    # also pass if admin



    return render(request, 'lfs/index.html', context_dict)


@login_required
def user_contact_admin(request, userid):
    """ User contacts an admin """
    pass

@login_required
def leaderboard(request):
    """ Website leaderboard containing 'all' users """
    """ add top 20 users with progress """
    context_dict = {}

    # pass which navbar tab is active
    context_dict['nbar'] = 'leaderboard'

    user = request.user
    if not user.is_staff:
        teacher = Teacher.objects.filter(user=user)[0]
        context_dict['teacher'] = teacher
    all_users = User.objects.all()

    takers_record = Takers.objects.all()
    # teacher's overall progress =
    # (sum of progress in all modules / # modules taken)
    modules_taken_count = takers_record.filter(user=user).count()
    if modules_taken_count != 0:
        context_dict['overall_progress'] = reduce(lambda x,y: x+y, [i.progress for i in takers_record if i.user==user], 0) / modules_taken_count
    else:
        context_dict['overall_progress'] = 0

    all_modules = Module.objects.all()
    # pass all modules as a dict with dict(module_name : [(name, progress)])
    context_dict['leaderboards'] = {str(i.title) : [(j.user, j.progress)for j in takers_record if j.module==i] for i in all_modules}

    # also pass total number of modules available throughout the platform
    context_dict['modules_total'] = Module.objects.all().count()

    # completed modules
    context_dict['modules_completed'] = {i.module : i.progress for i in takers_record if i.user==user and i.progress == 100}

    # pass per-user overall progress as:
    # { username : overall_progress }
    context_dict['all_users_overall_progress'] = {}

    for j in all_users:
        modules_taken_count = takers_record.filter(user=j).count()
        if modules_taken_count != 0:
            context_dict['all_users_overall_progress'].update({j: reduce(lambda x,y: x+y, [i.progress for i in takers_record if i.user==j], 0) / modules_taken_count})

        else:
            context_dict['all_users_overall_progress'].update({j:0})


    return render(request, 'lfs/leaderboard.html', context_dict)

def profile(request, userid):
    """ Profile of selected user """
    context_dict = {}

    # pass which navbar tab is active
    context_dict['nbar'] = 'profile'

    user = User.objects.get(id=userid)
    context_dict['profile_user_id'] = user.id

    # add user details to the context dictionary
    if not user.is_staff:
        context_dict.update(get_profileDetails(request, user.username))
        teacher = Teacher.objects.filter(user=user)[0]
        context_dict['teacher'] = teacher

    takers_record = Takers.objects.all()
    # teacher's overall progress =
    # (sum of progress in all modules / # modules taken)
    modules_taken_count = takers_record.filter(user=user).count()
    if modules_taken_count != 0:
        context_dict['overall_progress'] = reduce(lambda x,y: x+y, [i.progress for i in takers_record if i.user==user], 0) / modules_taken_count
    else:
        context_dict['overall_progress'] = 0

    # pass all modules taken by user as a dict(module_name : progress)
    context_dict['modules_progress'] = {str(i.module.title) : i.progress for i in takers_record if i.user==user}

    # also pass total number of modules available throughout the platform
    context_dict['modules_total'] = Module.objects.all().count()

    # completed modules
    context_dict['modules_completed'] = {i.module : i.progress for i in takers_record if i.user==user and i.progress == 100}

    return render(request, 'lfs/profile.html', context_dict)

@login_required
def edit_profile(request, userid):
    """ Editing user profile """
    context_dict = {}

    # pass which navbar tab is active
    context_dict['nbar'] = 'profile'

    user = User.objects.get(id=userid)

    # prevent non-admins from editing random profiles
    if user != request.user:
        if not user.is_superuser:
            # just redisplay the profile
            return HttpResponseRedirect('/lfs/profile/{0}/'.format(user.id))


    if not user.is_staff:
        teacher = Teacher.objects.filter(user=user)[0]
        context_dict['teacher'] = teacher
    changed = False

    # get the instance of the user
    context_dict['user_form'] = UserForm(instance = user)
    context_dict['teacher_form'] = TeacherForm(instance = teacher)

    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        user_form = UserForm(request.POST, request.FILES, instance= user)
        teacher_form = TeacherForm(request.POST, request.FILES, instance= teacher)
        # check if password is correct
        if user.check_password(user_form.data['password']):
            if  user_form.is_valid():
                if teacher_form.is_valid():
                    user = user_form.save()

                    user.set_password(user.password)
                    user.save()

                    teacher = teacher_form.save()
                    teacher.save()

                    username = request.POST['username']
                    password = request.POST['password']
                    user = authenticate(username=username, password=password)
                    login(request, user)

                    context_dict.update(get_profileDetails(request, username))
                    context_dict['user_form'] = UserForm(instance = user)
                    context_dict['teacher_form'] = TeacherForm(instance = teacher)
                    changed = True
                else:
                    context_dict['message'] = teacher_form.errors
            else:
                context_dict['message'] = user_form.errors
        else:
            # used to inform the user to input the password
            context_dict['message'] = "Please enter correct password to save changes"

    if changed:
        return HttpResponseRedirect('/lfs/profile/{0}/'.format(user.id))


    return render(request, 'lfs/modify/edit_profile.html', context_dict) #Does this work?

def change_password(request):
    """ Change Password """

    context_dict = {}
    user = request.user
    context_dict['nbar'] = 'profile'
    context_dict['userid'] = user.id

    password_form = PasswordChangeForm(user=user, data=request.POST)

    context_dict['password_form'] = password_form

    if request.method == 'POST':
        print
        users_password = user.password
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        if user.check_password(old_password):
            if new_password == confirm_password:
                if password_form.is_valid():

                    user.set_password(new_password)
                    user.save()

                    user = authenticate(username=user.username, password=new_password)
                    login(request, user)
                    return HttpResponseRedirect('/lfs/profile/{0}/'.format(user.id))
                else:
                    context_dict['message'] = password_form.errors
            else:
                context_dict['message'] = "New passwords don't match"
        else:
            context_dict['message'] = "Current password is incorrect"

    return render(request, 'lfs/modify/change_password.html', context_dict) #TODO not sure what to put here

def get_profileDetails(request, username):
    """ Gets user info needed for displaying profile"""
    context_dict = {}

    user = User.objects.get(username = username)

    teacher = Teacher.objects.get(user = user)

    context_dict['username'] = user.username
    context_dict['first_name'] = user.first_name
    context_dict['last_name'] = user.last_name
    context_dict['bio'] = teacher.bio
    context_dict['school'] = teacher.school

    return context_dict

@login_required
def forum(request):
    """ shows forum template """
    #context_dict = {}

    # get currently logged in user
    #user = request.user
    #if not user.is_staff:
    #    teacher = Teacher.objects.filter(user=user)[0]
    #    context_dict['teacher'] = teacher

    # pass which navbar tab is active
    #context_dict['nbar'] = 'forum'

    #takers_record = Takers.objects.all()
    # teacher's overall progress =
    # (sum of progress in all modules / # modules taken)
    #modules_taken_count = takers_record.filter(user=user).count()
    #if modules_taken_count != 0:
    #    context_dict['overall_progress'] = reduce(lambda x,y: x+y, [i.progress for i in takers_record if i.user==user], 0) / modules_taken_count
    #else:
    #    context_dict['overall_progress'] = 0

    # pass all modules taken by user as a dict(module_name : progress)
    #context_dict['modules_progress'] = {i.module : i.progress for i in takers_record if i.user==user}

    # also pass total number of modules available throughout the platform
    #context_dict['modules_total'] = Module.objects.all().count()

    # completed modules
    #context_dict['modules_completed'] = {i.module : i.progress for i in takers_record if i.user==user and i.progress == 100}

    #return render(request, 'lfs/forum.html', context_dict)
    return HttpResponseRedirect('/forum/')


@login_required
def user_subscription(request, userid):
    """ Subscription service """
    pass

@login_required
def pick_module(request, moduleid):
    """ Allows user to modify their module choices by enrolling in a module """
    user = request.user
    module = Module.objects.get(id = moduleid)

    if not Takers.objects.filter(user = user, module = module).exists():
        taker = Takers.objects.create(user = user, module = module)

    return HttpResponseRedirect('/lfs/modules/')

@login_required
def drop_module(request, moduleid):
    """ Allows user to modify their module choices by unenrolling from a module"""
    user = request.user
    module = Module.objects.get(id = moduleid)

    if Takers.objects.filter(user = user, module = module).exists():
        Takers.objects.filter(user = user, module = module).delete()

    return HttpResponseRedirect('/lfs/modules/')


# -------------------- Modules Functionality ----------------------
def modules(request):
    """ All available modules """
    context_dict = {}
    context_dict['modules'] = []  # modules_not_taken
    context_dict['modules_taken'] = []
    context_dict['is_admin'] = False
    modules = Module.objects.all()

    #check if user is logged in
    if request.user.is_authenticated():
        user = request.user
        if Administrator.objects.filter(user = user).exists():
            context_dict['is_admin'] = True
            for m in modules:
                context_dict['modules'].append(m)

        # if user is a teacher split modules into taken and not taken for display order
        elif Teacher.objects.filter(user = user).exists():
            teacher = Teacher.objects.get(user = user)
            for m in modules:
                if user in m.taker.all():
                    context_dict['modules_taken'].append(m)
                else:
                    context_dict['modules'].append(m)


    return render(request, 'lfs/modules.html', context_dict)


def download_content(request, contentid):
    """ View for downloading static content """

    content_file = ContentFile.objects.filter(id=contentid)[0]

    # update click count
    content_file.clicks = content_file.clicks + 1
    content_file.save()

    filename = str(content_file.file)
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)

    return response


def module(request, moduleid):
    """ A particular module's contents """

    context_dict = {}
    module = Module.objects.get(id=moduleid)
    context_dict['module_title'] = module.title
    context_dict['module_id'] = moduleid
    if request.user.is_authenticated():
        user = request.user
        if Administrator.objects.filter(user = user).exists():
            context_dict['is_admin'] = True


    context_dict['pages'] = module.page_set.all()

    # count user hits
    hit_count_obj = HitCount.objects.get_for_object(module)
    hit_count_response = HitCountMixin.hit_count(request, hit_count_obj)
    context_dict['visits'] = module.hit_count.hits

    # Pages query returns ordered tuple (no need to label each page)
    context_dict['module_pages'] = tuple(i for i in Page.objects.filter(module=module))

    try:
        context_dict['user_progress_on_module'] = Takers.objects.get(user=request.user, module=module).progress
    except ObjectDoesNotExist:
        # if user isn't taking this module -> 0 progress
        context_dict['user_progress_on_module'] = 0

    context_dict['user_modules'] = tuple(i.module for i in Takers.objects.filter(user=request.user))

    context_dict['module_downloadable'] = tuple(i for i in ContentFile.objects.filter(module=module))


    return render(request, 'lfs/content.html', context_dict)


def update_progress(request, moduleid, pagenum):
    """ Updates the progress of a user while reading module content """
    #get user and module relation
    user = request.user
    module = Module.objects.get(id = moduleid)
    # if user has not finished all the pages
    response = render(request, 'lfs/content.html', {'module_id': moduleid})
    # get total number of pages
    pages_count = float(module.page_set.count());
    if user.is_authenticated():
        taker = Takers.objects.get(user=user, module=module)
        if taker.progress < 50:
            progress = 1.0
            # get current page/ all pages ratio
            progress = (float(pagenum) + 1.0)/pages_count
            taker.progress = 50*progress
            taker.save()
    else:
        title = str(module.title).replace(' ', '_')
        current_progress = int(request.COOKIES.get(title, '0'))
        if current_progress < 50:
            progress = (float(pagenum) + 1.0)/pages_count * 50
            if current_progress < progress:
                response.set_cookie(title, int(progress))

    return response


# ----------------------- Messaging Functionality ---------------------

def user_messages(request, userid):
    """ View of a user's message history """
    pass


@login_required
def message_send(request, messageid):
    """ User sends a message """
    pass


@login_required
def message(request, messageid):
    """ View a particular message (from the inbox) """
    pass

# ----------------------- Admin Pages -----------------------------------

@login_required
def admin_guide(request):
    """ A guide to administering the website """

    context_dict = {}

    if request.user.is_authenticated():
        user = request.user
        if Administrator.objects.filter(user = user).exists():
            context_dict['is_admin'] = True

    # pass which navbar tab is active
    context_dict['nbar'] = 'admin_guide'

    return render(request,'lfs/admin_guide.html', context_dict)

# ----------------------- Trial Pages -----------------------------------

def trial_dashboard(request):
    """ Trial dashboard with all trial modules """

    context_dict = {}

    context = RequestContext(request)

    context_dict['trial'] = True

    modules = Module.objects.filter(trial=True)
    modules_count = Module.objects.filter(trial=True).count()

    # pass all trial modules a dict(module_name : progress)
    context_dict['modules_progress'] = {i : int(request.COOKIES.get(str(i).replace(' ', '_'), '0')) for i in modules}
    if modules_count != 0:
        context_dict['overall_progress'] = reduce(lambda x,y: x+y, [value for key, value in context_dict['modules_progress'].iteritems()], 0) / modules_count
    else:
        context_dict['overall_progress'] = 0

    # also pass total number of modules available throughout the platform
    context_dict['modules_total'] = Module.objects.all().count()

    # assign cookie values
    cookie_lifetime = 60 * 60 # all cookies should last for an hour

    response = render_to_response('lfs/trial/index.html', context_dict, context)

    for key, value in context_dict['modules_progress'].iteritems():
        title = str(key).replace(' ', '_')
        response.set_cookie(title, value, max_age=cookie_lifetime)

    return response

def trial_module(request, moduleid):
    """ A particular trial module's contents """

    context_dict = {}
    context = RequestContext(request)

    module = Module.objects.get(id=moduleid)

    # if module is not a trial module, redirect to welcome page
    if not module.trial:
        return HttpResponseRedirect('/lfs/')

    context_dict['module_title'] = module.title
    context_dict['module_id'] = moduleid
    context_dict['pages'] = module.page_set.all()

    # Pages query returns ordered tuple (no need to label each page)
    context_dict['module_pages'] = tuple(i for i in Page.objects.filter(module=module))
    title = str(module.title).replace(' ', '_')
    context_dict['user_progress_on_module'] = int(request.COOKIES.get(title, '0'))
    print context_dict['user_progress_on_module'], int(request.COOKIES.get(title, '0'))
    context_dict['user_modules'] = Module.objects.filter(trial=True)

    context_dict['module_downloadable'] = tuple(i for i in ContentFile.objects.filter(module=module))

    # assign cookie values
    cookie_lifetime = 60 * 60 # all cookies should last for an hour

    response = render_to_response('lfs/trial/content.html', context_dict, context)
    response.set_cookie(title, context_dict['user_progress_on_module'], max_age=cookie_lifetime)

    return response
