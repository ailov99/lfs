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
from lfs_quiz.forms import *

# Logg stuff
import logging

logging.basicConfig(filename='wtf.log', level=logging.INFO)
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
        modules_lookup.append({'mod_title': mod.title, 'hit_count': mod.hit_count.hits_in_last(days=7)})

    # 2. New website registrations in last 7 days
    regs_lookup = []
    for i in range(0, 7):
        d_date = date.today() - timedelta(days=i)
        js_date = d_date.strftime('%d-%m-%Y')  # d3-parsable format
        # construct array of objects
        d_rec = UserRegistrations.objects.get_or_create(time=d_date)[0]
        regs_lookup.append({'date': js_date, 'reg_count': d_rec.count})

    # 3. Anonymous user hits (visits) of the welcome page in last 7 days
    anons_lookup = []
    for i in range(0, 7):
        d_date = date.today() - timedelta(days=i)
        js_date = d_date.strftime('%d-%m-%Y')  # d3-parsable format
        # construct array of objects
        d_rec = AnonHits.objects.get_or_create(time=d_date)[0]
        anons_lookup.append({'date': js_date, 'anon_hits_count': d_rec.count})

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

            return HttpResponseRedirect('/lfs_admin/edit_module/' + str(module.id) + '/')

        else:
            print module_form.errors

    return render(request, 'lfs/modify/add_module.html', context_dict)


def edit_module(request, moduleid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    module = Module.objects.get(id=moduleid)

    context_dict['module_id'] = moduleid
    if Quiz.objects.filter(module=module).exists():
        context_dict['quiz'] = Quiz.objects.get(module=module)
    else:
        context_dict['quiz'] = None

    context_dict['pages'] = []

    pages = module.page_set.all()

    for p in pages:
        context_dict['pages'].append(p)

    context_dict['module_downloadable'] = tuple(i for i in ContentFile.objects.filter(module=module))

    context_dict['content_form'] = ContentForm()

    context_dict['module_form'] = ModuleForm(instance=module)

    if request.method == 'POST':
        module_form = ModuleForm(request.POST, request.FILES, instance=module)
        content_form = ContentForm(request.POST, request.FILES)

        if module_form.is_valid():
            module.save()

            if content_form.is_valid():
                content = content_form.save(commit=False)
                module.contentfile_set.add(content)
                content.save()
            else:
                print content_form.errors

            # redirect to module { url 'module' module.id}

            return HttpResponseRedirect('/lfs/module/' + moduleid + '/')

        else:
            print module_form.errors

    return render(request, 'lfs/modify/edit_module.html', context_dict)


def add_page(request, moduleid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['page_form'] = PageForm()
    context_dict['module_id'] = moduleid

    module = Module.objects.filter(id=moduleid)[0]

    if request.method == 'POST':
        page_form = PageForm(request.POST)
        if page_form.is_valid():
            page = page_form.save(commit=False)
            module.page_set.add(page)
            page.position = module.page_set.count()
            page.save()

            return HttpResponseRedirect('/lfs_admin/edit_module/' + str(moduleid) + '/')

        else:
            print page_form.errors
    return render(request, 'lfs/modify/add_page.html', context_dict)


def edit_page(request, pageid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['page_id'] = pageid
    page = Page.objects.get(id=pageid)
    moduleid = page.module.id

    context_dict['page_form'] = PageForm(instance=page)
    if request.method == 'POST':
        page_form = PageForm(request.POST, instance=page)
        if page_form.is_valid():

            page = page_form
            page.save()

            return HttpResponseRedirect('/lfs_admin/edit_module/' + str(moduleid) + '/')

        else:
            print "Error on editing page: " + str(page_form.errors)

    return render(request, 'lfs/modify/edit_page.html', context_dict)


# Delete page

def delete_page(request, pageid):
    page = Page.objects.get(id=pageid)
    page.delete()
    return HttpResponseRedirect('/lfs_admin/admin/')


def delete_module(request, moduleid):
    module = Module.objects.get(id=moduleid)
    module.delete()
    return HttpResponseRedirect('/lfs_admin/admin/')


def add_quiz(request, moduleid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['quiz_form'] = QuizForm()
    context_dict['module_id'] = moduleid

    module = Module.objects.filter(id=moduleid)[0]

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.module = module
            quiz.save()

            return HttpResponseRedirect('/lfs_admin/edit_quiz/' + str(quiz.id) + '/')

        else:
            print quiz_form.errors

    return render(request, 'lfs/modify/add_quiz.html', context_dict)


def edit_quiz(request, quizid):
    """ Admin can edit/add/remove quizzes """
    context_dict = {}
    context_dict['quiz_id'] = quizid
    quiz = Quiz.objects.get(id=quizid)
    moduleid = quiz.module.id
    context_dict['module_id'] = moduleid

    context_dict['tf_questions'] = TF_Question.objects.filter(quiz=quiz)
    context_dict['mc_questions'] = MCQuestion.objects.filter(quiz=quiz)

    context_dict['quiz_form'] = QuizForm(instance=quiz)
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, instance=quiz)
        if quiz_form.is_valid():
            quiz = quiz_form
            quiz.save()

            return HttpResponseRedirect('/lfs_admin/edit_module/' + str(moduleid) + '/')

        else:
            print "Error on editing page: " + str(quiz_form.errors)

    return render(request, 'lfs/modify/edit_quiz.html', context_dict)


def delete_quiz(request, quizid):
    quiz = Quiz.objects.get(id=quizid)
    quiz.delete()
    return HttpResponse('Quiz deleted')


def add_tfquestion(request, quizid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['tf_form'] = TFQuestionForm()
    context_dict['quiz_id'] = quizid

    quiz = Quiz.objects.filter(id=quizid)[0]

    if request.method == 'POST':
        tf_form = TFQuestionForm(request.POST)
        if tf_form.is_valid():
            tf = tf_form.save(commit=False)
            tf.save()
            tf.quiz.add(quiz)

            return HttpResponseRedirect('/lfs_admin/edit_quiz/' + str(quizid) + '/')

        else:
            print tf_form.errors

    return render(request, 'lfs/modify/add_tfquestion.html', context_dict)


def edit_tfquestion(request, tfid, quizid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['tf_id'] = tfid
    context_dict['quiz_id'] = quizid

    tf = TF_Question.objects.get(id=tfid)
    context_dict['tf_form'] = TFQuestionForm(instance=tf)

    if request.method == 'POST':
        tf_form = TFQuestionForm(request.POST, instance=tf)
        if tf_form.is_valid():
            tf = tf_form.save(commit=False)
            tf.save()

            return HttpResponseRedirect('/lfs_admin/edit_quiz/' + str(quizid) + '/')

        else:
            print tf_form.errors

    return render(request, 'lfs/modify/edit_tfquestion.html', context_dict)


def delete_tfquestion(request, tfid):
    tf = TF_Question.objects.get(id=tfid)
    tf.delete()
    return HttpResponse('Question deleted')


def add_mcquestion(request, quizid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['mc_form'] = MCQuestionForm()
    context_dict['answer_form'] = AnswerFormSet()
    context_dict['quiz_id'] = quizid

    quiz = Quiz.objects.filter(id=quizid)[0]

    if request.method == 'POST':
        mc_form = MCQuestionForm(request.POST)
        if mc_form.is_valid():
            mc = mc_form.save(commit=False)
            mc.save()
            mc.quiz.add(quiz)

            answer_formset = AnswerFormSet(request.POST, instance=mc)
            if answer_formset.is_valid():
                answer_formset.save()
            else:
                print answer_formset.errors

            return HttpResponseRedirect('/lfs_admin/edit_quiz/' + str(quizid) + '/')

        else:
            print mc_form.errors

    return render(request, 'lfs/modify/add_mcquestion.html', context_dict)


def edit_mcquestion(request, mcid, quizid):
    """ Admin can edit/add/remove modules """
    context_dict = {}
    context_dict['mc_id'] = mcid
    context_dict['quiz_id'] = quizid

    mc = MCQuestion.objects.filter(id=mcid)[0]

    context_dict['mc_form'] = MCQuestionForm(instance=mc)
    context_dict['answer_form'] = AnswerFormSet(instance=mc)
    if request.method == 'POST':
        mc_form = MCQuestionForm(request.POST, instance=mc)
        if mc_form.is_valid():
            mc = mc_form.save(commit=False)
            mc.save()

            answer_formset = AnswerFormSet(request.POST, instance=mc)
            if answer_formset.is_valid():
                answer_formset.save()
            else:
                print answer_formset.errors

            return HttpResponseRedirect('/lfs_admin/edit_quiz/' + str(quizid) + '/')

        else:
            print mc_form.errors

    return render(request, 'lfs/modify/edit_mcquestion.html', context_dict)


def delete_mcquestion(request, mcid):
    mc = MCQuestion.objects.get(id=mcid)
    answers = Answer.objects.filter(question=mc)
    for answer in answers:
        answer.delete()
    mc.delete()
    return HttpResponse('Question deleted')


@login_required
def user_list(request):
    context_dict = {}
    context_dict['users'] = User.objects.all()
    user = request.user
    takers_record = Takers.objects.all()
    modules_taken_count = takers_record.filter(user=user).count()
    if modules_taken_count != 0:
        context_dict['overall_progress'] = reduce(lambda x, y: x + y,
                                                  [i.progress for i in takers_record if i.user == user],
                                                  0) / modules_taken_count
    else:
        context_dict['overall_progress'] = 0
    return render(request, 'lfs/modify/user_list.html', context_dict)


@login_required
def promote_user(request, userid):
    user = User.objects.get(id=userid)

    if Administrator.objects.filter(user=user).exists():
        admin = Administrator.objects.get(user=user)
        admin.delete()
    else:
        admin = Administrator.objects.create(user=user)
    return HttpResponseRedirect('/lfs_admin/user_list/')
