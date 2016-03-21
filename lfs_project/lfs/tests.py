from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from models import Teacher, Module, Takers, Page, ContentFile


class UserAppTests(TestCase):

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

    def test_user_registration_model(self):
        """
          On registering, a new user is created, tied to an 'empty'
          Teacher model
        """

        # Assure DB is properly populated with correct data
        self.assertEqual(User.objects.filter(username="jdoe").count(), 1)
        self.assertEqual(Teacher.objects.filter(user__username="jdoe").count(), 1)


    def test_user_registration_api(self):
        """
          Correct registration POST will result in a properly populated
          DB with both User and Teacher
        """
        # attempt to send data which does not comply with the Terms and Cond
        response = self.c.post('/lfs/register/', {'username': 'jstorer',
                                                  'email': 'jstorer@gmail.com',
                                                  'first_name': 'Jeremy',
                                                  'last_name': 'Storer',
                                                  'password': '12345abcD',
                                                  'terms' : False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='jstorer').count(), 0)

        
        # send terms-compliant data for a dummy user
        response = self.c.post('/lfs/register/', {'username': 'jstorer',
                                                  'email': 'jstorer@gmail.com',
                                                  'first_name': 'Jeremy',
                                                  'last_name': 'Storer',
                                                  'password': '12345abcD',
                                                  'terms' : True})


        # Should be redirected to login page
        self.assertRedirects(response, '/lfs/login/')

        # Assure DB is properly populated  with correct data
        self.assertEqual(User.objects.filter(username='jstorer').count(), 1)

        new_user = User.objects.filter(username='jstorer')[0]
        self.assertEqual(new_user.first_name, 'Jeremy')
        self.assertEqual(new_user.last_name, 'Storer')

        self.assertEqual(Teacher.objects.filter(user__username='jstorer').count(), 1)

        new_teacher = Teacher.objects.filter(user__username='jstorer')[0]
        self.assertEqual(new_teacher.bio, '')
        self.assertEqual(new_teacher.school, '')


    def test_user_login(self):
        """
          A user who is in the DB should be able to log in (as a teacher)
        """

        # send a POST with username/pass
        response = self.c.post('/lfs/login/', {'username': 'jdoe', 'password': '123'})

        # should be at dashboard
        self.assertRedirects(response, '/lfs/dashboard/')


    def test_user_logout(self):
        """
          An existing user should be able to log out if currently logged in
        """

        # log in (should redirect)
        login_response = self.c.post('/lfs/login/', {'username': 'jdoe', 'password': '123'})
        self.assertEqual(login_response.status_code, 302)

        logout_response = self.c.post('/lfs/logout/', {})
        self.assertRedirects(logout_response, '/lfs/login/')


    def test_user_dashboard(self):
        """
          A logged in user should see their dashboard, with all
          modules taken, their per-module and overall progress
        """

        user_two = User.objects.create_user("tsinger", "tsinger@gmail.com", "123",
                                            first_name="Tim", last_name="Singer")

        teacher_two = Teacher.objects.create(user=user_two, bio="I teach programming",
                                             school="Glasgow School")

        # populate DB with modules taken by user, with random progress stats
        data = {"Introduction to Sustainable Development" : 12,
                "What does it all mean?" : 59,
                "How to teach students" : 77}
        dummy_modules = []

        for key in data:
            module = Module.objects.create(title=key)
            dummy_modules.append(module)
            Takers.objects.create(user=self.user, module=module, progress=data[key])

        # assign two of the modules to the other user (with different progress)
        Takers.objects.create(user=user_two, module=Module.objects
                              .filter(title="What does it all mean?")[0],
                              progress=99)
        Takers.objects.create(user=user_two, module=Module.objects
                              .filter(title="How to teach students")[0],
                              progress=32)

        # log in
        self.c.login(username="jdoe", password="123")

        # dashboard GET
        dashboard_response = self.c.get('/lfs/dashboard/')

        # check modules
        self.assertEqual(set(dashboard_response.context['modules_progress'].keys()),
                         set(dummy_modules))

        # check per-module progress
        for key in dummy_modules:
            self.assertEqual(dashboard_response.context['modules_progress'][key],
                             data[key.title])

        # check overall progress
        self.assertEqual(dashboard_response.context['overall_progress'],
                         reduce(lambda x,y: x+y, [data[key] for key in data]) / len(data))


    def test_module_content_viewable_by_user(self):
        """
          A user should be able to see all available modules' contents
        """

        # Assign random modules to test user
        mod1 = Module.objects.create(title="First Module")
        mod2 = Module.objects.create(title="Second Module")
        Takers.objects.create(user=self.user, module=mod1)
        Takers.objects.create(user=self.user, module=mod2)

        # log in
        self.c.login(username="jdoe", password="123")

        # module that our user has taken (not necessary for viewing)
        module = Module.objects.create(title="Third Module")
        Takers.objects.create(user=self.user, module=module)

        # assign some pages to module
        Page.objects.create(module=module,
                            position=0,
                            section="First Page",
                            content="""
                            Vivamus sit amet auctor nisl, in auctor augue.
                            Nullam a purus eu erat semper eleifend quis a ex.
                            Phasellus a tortor quis lectus ultrices vestibulum sit amet ac nunc.
                            In rutrum hendrerit lorem non consequat. Ut malesuada orci ligula,
                            eu dapibus est viverra sed. Fusce lacinia ante non porta cursus.
                            """)

        Page.objects.create(module=module,
                            position=1,
                            section="Second Page",
                            content="""
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                            Nunc pellentesque nec orci dignissim congue. Quisque nec interdum augue.
                            Praesent ultricies felis nec nulla gravida tempor. In consequat aliquam
                            congue.
                            """)

        # module GET
        module_response = self.c.get('/lfs/module/{0}/'.format(module.id))

        # check currently viewable module
        self.assertEqual(module_response.context['module_title'],module.title)
        self.assertEqual(set(module_response.context['module_pages']),
                         set(tuple(i for i in module.page_set.all())))

        self.assertContains(module_response, module.title)
        # Should be on first page by default
        self.assertContains(module_response, module.page_set.all()[0].section)

        # Should be tabbed on currently viewed Module by default
        # so all sections of that module should be displayed (navigatable)
        for page in module.page_set.all():
            self.assertContains(module_response, page.section)

        # all other user taken modules should be visible
        user_module_junctions = tuple(i.module for i in Takers.objects.filter(user=self.user))
        for mod in user_module_junctions:
            self.assertContains(module_response, mod.title)


    def test_user_leaderboard(self):
        """
           Users should be able to see a leaderboard of all users using the website
        """

        # log in
        self.c.login(username="jdoe", password="123")

        # assign some modules to dummy user to check progress
        mod_one = Module.objects.create(title="First Module")
        mod_two = Module.objects.create(title="Second Module")
        Takers.objects.create(user=self.user, module=mod_one, progress=55)
        Takers.objects.create(user=self.user, module=mod_two, progress=35)

        # leaderboards GET
        response = self.c.get('/lfs/leaderboard/')

        # check all users are passed with their progress
        user_count = Teacher.objects.all().count()
        self.assertEqual(len(response.context['all_users_overall_progress']), user_count)
        # check progress
        self.assertEqual(response.context['all_users_overall_progress'][self.user],
                         45)


    def test_user_profile(self):
        """
        A registered user should be able to inspect their own as well
        as others' profiles
        """

        user_j = User.objects.create_user("jstorer", "jstorer@gmail.com", "123",
                                          first_name="Jeremy", last_name="Storer")

        teacher_j = Teacher.objects.create(user=user_j, bio="I am a teacher",
                                           school="Glasgow University")

        # log in
        self.c.login(username="jdoe", password="123")

        # inspect own profile
        own_response = self.c.get('/lfs/profile/{0}/'.format(self.user.id))

        self.assertEqual(self.teacher, own_response.context['teacher'])

        # inspect someone else's profile
        else_response = self.c.get('/lfs/profile/{0}/'.format(user_j.id))

        self.assertEqual(teacher_j, else_response.context['teacher'])


    def test_user_get_edit_profile(self):
        """
        Logged in users should be able to edit their own profiles
        """

        user_j = User.objects.create_user("jstorer", "jstorer@gmail.com", "123",
                                          first_name="Jeremy", last_name="Storer")

        teacher_j = Teacher.objects.create(user=user_j, bio="I am a teacher",
                                           school="Glasgow University")

        # log in
        self.c.login(username="jdoe", password="123")

        # test editing own profile
        own_response = self.c.get('/lfs/profile/{0}/edit/'.format(self.user.id))

        self.assertEqual(own_response.context['teacher'], self.teacher)
        self.assertEqual(own_response.context['user_form'].instance, self.user)

        # test editing some else's (not allowed)
        else_response = self.c.get('/lfs/profile/{0}/edit/'.format(user_j.id))

        self.assertRedirects(else_response, '/lfs/profile/{0}/'.format(user_j.id))


    def test_user_post_edit_profile(self):
        """
        Logged in users should be able to edit their own profiles
        """

        user_j = User.objects.create_user("jstorer", "jstorer@gmail.com", "123",
                                          first_name="Jeremy", last_name="Storer")

        teacher_j = Teacher.objects.create(user=user_j, bio="I am a teacher",
                                           school="Glasgow University")

        # log in
        self.c.login(username="jdoe", password="123")

        own_response = self.c.post('/lfs/profile/{0}/edit/'.format(self.user.id),
                                   {'username' : 'jdoe',
                                    'password' : '123' ,
                                    'first_name' : 'Gethin',
                                    'last_name' : 'Gay',
                                    'bio' : 'new bio',
                                    'school' : 'Caledonian'})


    def test_user_change_password(self):
        """
        A user should be able to request change
        of their password
        """
        self.c.login(username="jdoe", password="123")

        new_p = 'ab789ABC'
        old_p = '123'

        # TODO: enable once GET requests are handled in views

        # Wrong old password
        #response = self.c.post('/lfs/change_password/{0}'.format(self.user.id),
         #                      {'old_password' : '01234',
         #                      'new_password' : new_p,
         #                       'confirm_new_password' : new_p})

        #self.assertEqual(self.user.password, old_p)

        # Wrong new password confirmation
        #response = self.c.post('/lfs/change_password/{0}'.format(self.user.id),
        #                       {'old_password' : old_p,
        #                        'new_password' : new_p,
        #                        'confirm_new_password' : '6789'})

        #self.assertEqual(self.user.password, old_p)

        # Proper
        response = self.c.post('/lfs/change_password/',
                               {'old_password' : old_p,
                                'new_password1' : new_p,
                                'new_password2' : new_p})


        self.assertRedirects(response, '/lfs/profile/{0}/'.format(self.user.id))
        self.c.logout()
        self.assertEqual(self.c.login(username="jdoe", password=old_p),
                         False)
        self.assertEqual(self.c.login(username="jdoe", password=new_p),
                         True)



    def test_all_modules_viewable_by_user(self):
        """
        A user should be able to see all available modules
        in order to pick/modify his choices
        """

        # Add modules
        mods = ["First Module", "Introduction Module", "Random stuff",
                "Fillers", "How to teach", "Sustainable energy"]

        for t in mods:
            Module.objects.create(title=t)

        # Assign a random module to user
        mod = Module.objects.all()[0]
        Takers.objects.create(module=mod, user=self.user)

        self.c.login(username="jdoe", password="123")
        response = self.c.get('/lfs/modules/')

        self.assertEqual(response.context['is_admin'], False)
        self.assertEqual(len(response.context['modules']), len(mods) - 1)
        self.assertEqual(len(response.context['modules_taken']), 1)
        self.assertEqual(response.context['modules_taken'][0], mod)


    def test_user_pick_module(self):
        """
        A user should be able to pick modules at will
        """
        # Random unassigned module
        new_mod = Module.objects.create(title="Unpicked module")

        self.c.login(username="jdoe", password="123")
        response = self.c.get('/lfs/pick_module/{0}/'.format(new_mod.id))

        self.assertRedirects(response, '/lfs/modules/')
        self.assertEqual(Takers.objects.filter(user=self.user,
                                               module=new_mod).exists(), True)


    def test_user_drop_module(self):
        """
        A user should be able to drop modules at will
        """
        # Create a module and assign it to user
        user_mod = Module.objects.create(title="Picked module")
        Takers.objects.create(user=self.user, module = user_mod)

        self.c.login(username="jdoe", password="123")
        response = self.c.get('/lfs/drop_module/{0}/'.format(user_mod.id))

        self.assertRedirects(response, '/lfs/modules/')
        self.assertEqual(Takers.objects.filter(user=self.user,
                                               module=user_mod).exists(), False)
