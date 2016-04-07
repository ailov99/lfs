from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from lfs_admin.models import Administrator, UserRegistrations
from lfs.models import Teacher, Module, ContentFile, Page
from lfs_quiz.models import Quiz, TF_Question, MCQuestion, Answer
from datetime import date
import json


class AdminAppTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user("jdoe",
                                             "jdoe@gmail.com",
                                             "123",
                                             first_name="John",
                                             last_name="Doe")
        self.teacher = Teacher.objects.create(user=self.user,
                                              bio="I am a dummy teacher",
                                              school="Dummy School")
        self.admin = Administrator.objects.create(user=self.user,
                                                  bio=self.teacher.bio)

        
    def test_admin_model(self):
        """
        Test for the admin model
        NOTE: this is needed largely due to coverage
        """
        self.assertEqual(self.admin.user, self.user)
        self.assertEqual(self.admin.bio, self.teacher.bio)
        self.assertEqual(str(self.admin), self.user.username)

        
    def test_user_registration_model(self):
        """
        Test for the model representing a new User's registration
        NOTE: this is needed largely due to coverage
        """
        user_reg = UserRegistrations()
        for i in range(0,5):
            user_reg.inc()

        self.assertEqual(user_reg.count, 5)
        self.assertEqual(str(user_reg), str(user_reg.time))


    def test_admin_welcome_page(self):
        """
        An admin should see a welcome page when navigating
        to the admins' part of the website
        NOTE: this is currently not an intended feature
        """
        self.c.login(username="jdoe", password="123")
        response = self.c.get('/lfs_admin/')

        self.assertContains(response, "Hello world!")

        
    def test_admin_stats(self):
        """
         An admin of the website must have exclusive access to a
         page with website statistics
        """

        mods = []
        for title in ["Introduction", "Random Module", "Conclusion"]:
            mods.append(Module.objects.create(title=title))

        # set up module hits:
        # 0 / 10 / 20
        hit_num = 0
        for mod in mods:
            for i in range(0, hit_num):
                mod.hit_count.increase()
            hit_num += 10

        # set up new user registrations
        UserRegistrations.objects.create(time=date.today(), count=10)
            
        self.c.login(username="jdoe", password="123")
        response = self.c.get('/lfs_admin/stats/')
    
        self.assertEqual(response.status_code, 200)

        # check module hits JSON
        modules_data = json.loads(response.context['modules_data'])

        self.assertEqual(len(modules_data), len(mods))
        self.assertEqual(set(i['mod_title'] for i in modules_data),
                         set(i.title for i in mods))
        for record in modules_data:
            self.assertEqual(record['hit_count'],
                             Module.objects.get(title=record['mod_title'])
                             .hit_count.hits_in_last(days=7))

            
        # check regs count JSON
        regs_data = json.loads(response.context['regs_data'])

        self.assertEqual(len(regs_data), 7)

        # scan for today's record
        for record in regs_data:
            if record['date'] == date.today().strftime('%d-%m-%Y'):
                self.assertEqual(record['reg_count'], 10)
        

                
    def test_admin_modules_viewable(self):
        """
        An admin should be able to see all modules
        """
        mods = ['Mod1', 'Mod2', 'Mod3']
        for title in mods:
            Module.objects.create(title=title)
            
        self.c.login(username="jdoe", password="123")
        response = self.c.get('/lfs_admin/admin/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['modules']),
                         set(Module.objects.all()))
        self.assertEqual(len(response.context['modules']),
                         len(mods))
        

    def test_admin_add_modules(self):
        """
        An admin should be able to add modules
        """
        self.c.login(username="jdoe", password="123")

        # GET
        response = self.c.get('/lfs_admin/add_module/')
        self.assertEqual(response.status_code, 200)

        # POST correct form
        response = self.c.post('/lfs_admin/add_module/',
                               {'title' : 'Test Module'})

        self.assertEqual(Module.objects.filter(title='Test Module').exists(),
                         True)
        self.assertRedirects(response,
                             '/lfs_admin/edit_module/{0}/'.format(Module.objects.get(title='Test Module').id))

        # POST incorrect form
        response = self.c.post('/lfs_admin/add_module/',
                               {'not_title' : '333'})
        self.assertEqual(response.status_code, 200)

    def test_admin_edit_module(self):
        """
        An admin should be able to edit modules
        """
        self.c.login(username="jdoe", password="123")

        mod = Module.objects.create(title="Test Module")

        # GET
        response = self.c.get('/lfs_admin/edit_module/{0}/'
                              .format(mod.id))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['module_id'], str(mod.id))
        self.assertEqual(set(context['pages']),
                         set(mod.page_set.all()))
        self.assertEqual(set(context['module_downloadable']),
                         set([i for i in ContentFile.objects.filter(module=mod)]))
        

        # POST (partially covered by GET checks)
        response = self.c.post('/lfs_admin/edit_module/{0}/'
                               .format(mod.id),
                               {'title' : 'Diff Title'})
        # re-query to get 'mod'
        self.assertEqual(Module.objects.all()[0].title, 'Diff Title')
        self.assertRedirects(response, '/lfs/module/{0}/'.format(mod.id))

        # POST - bad module form
        response = self.c.post('/lfs_admin/edit_module/{0}/'.format(mod.id),
                               {'something' : '333'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['module_id'], str(mod.id))
        self.assertEqual(set(context['pages']),
                         set(mod.page_set.all()))
        self.assertEqual(set(context['module_downloadable']),
                         set([i for i in ContentFile.objects.filter(module=mod)]))

        # POST - bad content form
        response = self.c.post('/lfs_admin/edit_module/{0}/'.format(mod.id),
                               {'title' : 3})
        self.assertRedirects(response, '/lfs/module/{0}/'.format(mod.id))

        
    def test_admin_add_page(self):
        """
        An admin should be able to add pages to modules
        """
        self.c.login(username="jdoe", password="123")
        mod = Module.objects.create(title="Test Module")
        
        # GET
        response = self.c.get('/lfs_admin/add_page/{0}/'.format(mod.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['module_id'], str(mod.id))

        
        # POST
        response = self.c.post('/lfs_admin/add_page/{0}/'.format(mod.id),
                               {'position' : 0,
                                'section' : 'Test Section',
                                'content' : 'TEST TEST TEST',
                                'module' : mod})

        #self.assertRedirects(response,
        #                     '/lfs_admin/edit_module/{0}/'.format(mod.id))
        #page = Page.objects.all()[0]
        #self.assertEqual(page.module, mod)
        #self.assertEqual(page.section, 'Test Section')
        #self.assertEqual(page.content, 'TEST TEST TEST')


    def test_admin_edit_page(self):
        """
        An admin should be able to edit pages
        """
        self.c.login(username="jdoe", password="123")
        mod = Module.objects.create(title="Test Module")
        page = Page.objects.create(module=mod,
                                   position=0,
                                   section="Test Section",
                                   content="TEST TEST TEST")
        
        # GET
        response = self.c.get('/lfs_admin/edit_page/{0}/'.format(page.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_id'], str(page.id))

        # POST
        response = self.c.post('/lfs_admin/edit_page/{0}/'.format(page.id),
                               {'position' : 1,
                                'section' : 'Altered Section',
                                'content' : 'Altered Content'})

        self.assertRedirects(response,
                             '/lfs_admin/edit_module/{0}/'.format(mod.id))
        # re-query for the page
        page = Page.objects.all()[0]
        self.assertEqual(page.section, 'Altered Section')

        # NOTE: Content is now BBCode object
        #self.assertEqual(page.content, 'Altered Content')


    def test_admin_delete_page(self):
        """
        An admin should be able to delete pages
        """
        self.c.login(username="jdoe", password="123")
        
        mod = Module.objects.create(title="Test Module")
        page = Page.objects.create(module=mod, position=0,
                                   section="", content="")

        response = self.c.get('/lfs_admin/delete_page/{0}/'.format(page.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Page.objects.filter(module=mod).exists(), False)


    def test_admin_delete_module(self):
        """
        An admin should be able to delete modules
        """
        self.c.login(username="jdoe", password="123")

        mod = Module.objects.create(title="Test Module")

        response = self.c.get('/lfs_admin/delete_module/{0}/'.format(mod.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Module.objects.filter(title="Test Module").exists(),
                         False)


    def test_admin_user_list_viewable(self):
        """
        An admin should be able to see a list of progress for users
        """
        self.c.login(username="jdoe", password="123")

        response = self.c.get('/lfs_admin/user_list/')

        self.assertEqual(response.status_code, 200)
        cont = response.context
        self.assertEqual(len(cont['users']), User.objects.all().count())
        self.assertEqual(cont['overall_progress'], 0)


    def test_admin_promote_user(self):
        """
        An admin should be able to promote users
        """
        self.c.login(username="jdoe", password="123")
        usr = User.objects.create_user("jsin",
                                       "jsin@gmail.com",
                                       "123",
                                       first_name="John",
                                       last_name="Doesn")
        
        # first promote user
        response = self.c.get('/lfs_admin/promote_user/{0}'.format(usr.id))

        self.assertRedirects(response, '/lfs_admin/user_list/')
        self.assertEqual(Administrator.objects.filter(user=usr).exists(),
                         True)

        # then demote user
        response = self.c.get('/lfs_admin/promote_user/{0}'.format(usr.id))

        self.assertRedirects(response, '/lfs_admin/user_list/')
        self.assertEqual(Administrator.objects.filter(user=usr).exists(),
                         False)

        
    def test_admin_add_quiz(self):
        """
        An admin should be able to add quizzes
        """
        mod = Module.objects.create(title="Test")

        response = self.c.post('/lfs_admin/add_quiz/{0}/'.format(mod.id),
                               {'title': "Test Quiz",
                                'description': "This is a test quiz",
                                'module': mod,
                                'pass_mark': 0})

        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Quiz.objects.all()[0].title, "Test Quiz")
        self.assertEqual(Quiz.objects.all()[0].description, "This is a test quiz")
        self.assertEqual(Quiz.objects.all()[0].module, mod)
        self.assertEqual(response.status_code, 302)


    def test_admin_edit_quiz(self):
        """
        An admin should be able to edit an already created quiz
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)

        response = self.c.post('/lfs_admin/edit_quiz/{0}/'.format(quiz.id),
                               {'title': "Unreal Quiz",
                                'description': "Not a test quiz",
                                'module': mod,
                                'pass_mark': 1})

        self.assertEqual(response.status_code, 302)
        quiz_new = Quiz.objects.filter(module=mod)[0]
        self.assertEqual(quiz_new.title, "Unreal Quiz")
        self.assertEqual(quiz_new.description, "Not a test quiz")
        self.assertEqual(quiz_new.pass_mark, 1)


    def test_admin_delete_quiz(self):
        """
        An admin should be able to delete quizzes
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)

        response = self.c.post('/lfs_admin/delete_quiz/{0}/{1}/'
                               .format(quiz.id, mod.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.count(), 0)


    def test_admin_add_tfquestion(self):
        """
        True-False question can be added to quizzes
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)

        response = self.c.post('/lfs_admin/add_tfquestion/{0}/'.format(quiz.id),
                               {'content': "Some question",
                                'module': mod,
                                'figure': None,
                                'explanation': "No explanation",
                                'correct': True})

        self.assertEqual(response.status_code, 200)
        #self.assertEqual(TF_Question.objects.count(), 1)
        #self.assertEqual(TF_Question.objects.all()[0].correct, True)
        #self.assertEqual(TF_Question.objects.all()[0].content, "Some question")


    def test_admin_edit_tfquestion(self):
        """
        True-False questions can be edited
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)
        tf = TF_Question.objects.create(content="Some question",
                                        module=mod,
                                        figure=None,
                                        explanation="No explanation",
                                        correct=False)

        response = self.c.post('/lfs_admin/edit_tfquestion/{0}/{1}/'
                               .format(tf.id, quiz.id),
                               {'content': "Some question",
                                'quiz': quiz,
                                'module': mod,
                                'figure': None,
                                'explanation': "No explanation",
                                'correct': True})

        self.assertEqual(response.status_code, 200)


    def test_admin_delete_tfquestion(self):
        """
        True-False questions can be deleted
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)
        tf = TF_Question.objects.create(content="Some question",
                                        module=mod,
                                        figure=None,
                                        explanation="No explanation",
                                        correct=False)

        response = self.c.post('/lfs_admin/delete_tfquestion/{0}/{1}/'
                               .format(tf.id, quiz.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TF_Question.objects.count(), 0)


    def test_admin_add_mcquestion(self):
        """
        Admins can add Multiple Choice questions
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)    
        response = self.c.post('/lfs_admin/add_mcquestion/{0}/'.format(quiz.id),
                               {'content': 'Some question',
                                'module': mod,
                                'figure': None,
                                'explanation': "No explanation",
                                'answer_order': 'htol'})

        self.assertEqual(response.status_code, 200)


    def test_admin_edit_mcquestion(self):
        """
        Admins can edit MC questions
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)
        mc = MCQuestion.objects.create(content="Some question",
                                        module=mod,
                                        figure=None,
                                        explanation="No explanation",
                                        answer_order="htol")

        response = self.c.post('/lfs_admin/edit_mcquestion/{0}/{1}/'
                               .format(mc.id, quiz.id),
                               {'content': "A question",
                                'module': mod,
                                'figure': None,
                                'explanation': "Explanation",
                                'answer_order': 'ltoh'})

        self.assertEqual(response.status_code, 200)


    def test_admin_delete_mcquestion(self):
        """
        MC Questions can be deleted by admins
        """
        mod = Module.objects.create(title="Test")
        quiz = Quiz.objects.create(title="Test Quiz",
                                   description="This is a test quiz",
                                   module=mod,
                                   pass_mark=0)
        mc = MCQuestion.objects.create(content="Some question",
                                        module=mod,
                                        figure=None,
                                        explanation="No explanation",
                                        answer_order="htol")
        Answer.objects.create(question = mc, content="No", correct=False)
        response = self.c.post('/lfs_admin/delete_mcquestion/{0}/'.format(mc.id))
        # TODO: check 404 status code
        #self.assertEqual(response.status_code, 302)
        #self.assertEqual(MCQuestion.objects.count(), 0)

        
        
    def test_admin_dashboard(self):
        """
        An admin should have access to a dashboard
        """
        self.c.login(username="jdoe", password="123")

        response = self.c.get('/lfs_admin/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")


    def test_admin_guide(self):
        """
        An admin should have access to a guide for 
        administering the web platform
        """
        self.c.login(username="jdoe", password="123")

        response = self.c.get('/lfs/admin_guide/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Guide")


    def test_change_colour_scheme(self):
        """
        An admin should be able to change the website's
        colour scheme at will
        """
        self.c.login(username="jdoe", password="123")

        response = self.c.get('/lfs_admin/change_colour_scheme/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Change Colour Scheme")

    












        
        
