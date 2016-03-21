from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from lfs.models import *
from lfs_admin.models import Administrator
from lfs_admin.models import UserRegistrations, AnonHits
from datetime import date, timedelta
import json
from django.contrib.auth.models import User
from lfs.forms import *

# Logg stuff
import logging
logging.basicConfig(filename='wtf.log',level=logging.INFO)
logger = logging.getLogger(__name__)


@login_required
def index(request):
    """ Welcome Page (probably shouldn't be accessible) """
    return HttpResponse("Hello world!")

@login_required
def admin_stats(request):
    """
    Site statistics for admins to see
    """
    context_dict = {}
    # 1. Page clicks per module in last 7 days
    modules_lookup = []
    for mod in Module.objects.all():
        # construct array of objects
        modules_lookup.append({'mod_title' : mod.title, 'hit_count' : mod.hit_count.hits_in_last(days=7)})

    # 2. New website registrations in last 7 days
    regs_lookup = []
    for i in range(0, 7):
        d_date = date.today() - timedelta(days=i)
        js_date = d_date.strftime('%d-%m-%Y') # d3-parsable format
        # construct array of objects
        d_rec = UserRegistrations.objects.get_or_create(time=d_date)[0]
        regs_lookup.append({'date' : js_date, 'reg_count' : d_rec.count})

    # 3. Anonymous user hits (visits) of the welcome page in last 7 days
    anons_lookup = []
    for i in range(0, 7):
        d_date = date.today() - timedelta(days=i)
        js_date = d_date.strftime('%d-%m-%Y') # d3-parsable format
        # construct array of objects
        d_rec = AnonHits.objects.get_or_create(time=d_date)[0]
        anons_lookup.append({'date' : js_date, 'anon_hits_count' : d_rec.count})

    # Pass to context as JSON ( map to JS [Object, Object] )
    context_dict['modules_data'] = json.dumps(modules_lookup)
    context_dict['regs_data'] = json.dumps(regs_lookup)
    context_dict['anon_hits_data'] = json.dumps(anons_lookup)

    return render(request, 'lfs/admin_stats.html', context_dict)

@login_required
def admin_dashboard(request):
    """ Generic dashboard for all admins """
    return HttpResponse("Admin Dashboard")


@login_required
def admin_guide(request):
    """ General guide to administering the website """
    return HttpResponse("Admin Guide")


@login_required
def change_colour_scheme(request):
    """ Change the website's colour scheme """
    return HttpResponse("Change Colour Scheme")
    
    
def admin(request):
    """ Admin see all modules, can add/remove/edit modules """
    context_dict = {}
    context_dict['modules'] = []
    modules = Module.objects.all()

    for m in modules:
        context_dict['modules'].append(m)

    return render(request, 'lfs/modify/admin.html', context_dict)

def add_module(request):
    """ Admin can edit/add/remove modules """

    context_dict = {}
    context_dict['module_form'] = ModuleForm()

    if request.method == 'POST':
        module_form = ModuleForm(request.POST)
        if module_form.is_valid():
            title = module_form.data['title']
            module = module_form.save()

            return HttpResponseRedirect('/lfs_admin/edit_module/'+str(module.id)+'/')

        else:
            print module_form.errors

    return render(request, 'lfs/modify/add_module.html', context_dict)

def edit_module(request, moduleid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    module = Module.objects.get(id=moduleid)

    context_dict['module_id'] = moduleid

    context_dict['pages'] = []

    pages = module.page_set.all()

    for p in pages:
        context_dict['pages'].append(p)

    context_dict['module_downloadable'] = tuple(i for i in ContentFile.objects.filter(module=module))

    context_dict['content_form'] = ContentForm()

    context_dict['module_form'] = ModuleForm(instance = module)
	
    if request.method == 'POST':
        module_form = ModuleForm(request.POST, request.FILES, instance= module)
        content_form = ContentForm(request.POST, request.FILES)

        if module_form.is_valid():
            module.save()

            if content_form.is_valid():
                content = content_form.save(commit = False)
                module.contentfile_set.add(content, bulk = False)
                content.save()
            else:
                print content_form.errors

            #redirect to module { url 'module' module.id}

            return HttpResponseRedirect('/lfs/module/'+moduleid+'/')

        else:
            print module_form.errors

    return render(request, 'lfs/modify/edit_module.html', context_dict)


def add_page(request, moduleid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['page_form'] = PageForm()
    context_dict['module_id'] = moduleid

    print moduleid

    module = Module.objects.filter(id = moduleid)[0]

    if request.method == 'POST':
        page_form = PageForm(request.POST)
        if page_form.is_valid():
            page =page_form.save(commit = False)
            module.page_set.add(page, bulk = False)
            page.position = module.page_set.count()
            page.save()

            return HttpResponseRedirect('/lfs_admin/edit_module/'+str(moduleid)+'/')

        else:
            print page_form.errors
    return render(request, 'lfs/modify/add_page.html', context_dict)

def edit_page(request, pageid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['page_id'] = pageid
    page = Page.objects.get(id=pageid)
    moduleid = page.module.id

    context_dict['page_form'] = PageForm(instance = page)
    if request.method == 'POST':
        page_form = PageForm(request.POST, instance = page)
        if page_form.is_valid():

            page = page_form
            page.save()

            return HttpResponseRedirect('/lfs_admin/edit_module/'+str(moduleid)+'/')

        else:
            print "Error on editing page: " + str(page_form.errors)

    return render(request, 'lfs/modify/edit_page.html', context_dict)

#Delete page

def delete_page(request, pageid):
   page = Page.objects.get(id = pageid)
   page.delete()
   return HttpResponse('Page deleted')

def delete_module(request, moduleid):
   module = Module.objects.get(id = moduleid)
   module.delete()
   return HttpResponse('Module deleted')
   
   
@login_required
def user_list(request):
    context_dict = {}
    context_dict['users'] = User.objects.all()
    user = request.user
    takers_record = Takers.objects.all()
    modules_taken_count = takers_record.filter(user=user).count()
    if modules_taken_count != 0:
        context_dict['overall_progress'] = reduce(lambda x,y: x+y, [i.progress for i in takers_record if i.user==user], 0) / modules_taken_count
    else:
        context_dict['overall_progress'] = 0
    return render(request, 'lfs/modify/user_list.html', context_dict)
	
	
@login_required
def promote_user(request, userid):

    user = User.objects.get(id=userid)
	
    if Administrator.objects.filter(user = user).exists():
        admin = Administrator.objects.get(user = user)
        admin.delete()
    else:
        admin = Administrator.objects.create(user = user)
    return HttpResponseRedirect('/lfs_admin/user_list/')
	