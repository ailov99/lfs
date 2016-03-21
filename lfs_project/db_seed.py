import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'lfs_project.settings'
django.setup()


import random
from lfs.models import Teacher, Module, Takers, Page, ModuleVideo, PageVideo, Picture, ContentFile
from lfs_quiz.models import Quiz, TF_Question, MCQuestion, Answer, Question
from django.contrib.auth.models import User
from django.core.files import File

names = [ 
        ("jdoe", "John", "Doe"),
        ("jstorer", "Jeremy", "Storer"),
        ("tsinger", "Tim", "Singer"),
        ("ggay", "Gethin", "Gay"),
        ("snorman", "Simon", "Norman"),
]

bios = [
        """
        I am a teacher at the Glasgow Academy.
        Willing to communicate with all colleagues in the region to exchange
        experience and discuss study materials.
        """,
        
        """
        Ex primary teacher looking to get back in the field.
        Interested in arts and sustainable development.
        """,
        
        """
        Please message me with questions about teaching... especially in the Fife area.
        I am looking forward to learning about this new sustainable development stuff.
        """,
        
        """
        """,
        
        """
        Just started learning about sustainable development!
        0755 33 24 65 contact me 
        """,
]

schools = [
        "Glasgow Academy",
        "Stirling High",
        "Edinburgh Primary 33",
        "Glasgow Arts Primary School",
        "Paisley Primary",
]

module_titles = [
        "Introduction",
        "What is sustainable development?",
        "How to teach effectively"
]

# Page contents in format (section, content)
page_contents = [
        ("What is this topic?",
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque hendrerit sem ut orci luctus, eget euismod sapien congue. 
        Maecenas tincidunt tempor dui eleifend fermentum. Curabitur eget posuere purus. Nulla facilisi. Integer vitae odio tortor. 
        Maecenas aliquet orci sit amet lorem posuere, vel malesuada magna egestas. Nulla nibh enim, ultricies nec tempor ut, 
        tempus id sapien. 
        
        Quisque dapibus nunc vitae ipsum blandit, pharetra bibendum lorem aliquam. Interdum et malesuada fames ac ante ipsum 
        primis in faucibus. Etiam sem orci, blandit interdum turpis eget, ornare condimentum ex. Praesent a nunc rhoncus, egestas 
        augue et, euismod velit. Duis convallis hendrerit mollis. Suspendisse tortor erat, ultrices sed tellus nec, vulputate tristique 
        dolor. Ut vehicula nisl vitae hendrerit dapibus. Donec dapibus fringilla ligula id condimentum. Phasellus porttitor arcu a 
        placerat laoreet. Curabitur sed sem sed diam feugiat pretium ac vitae nibh. Aenean non eleifend purus. Ut eget condimentum 
        diam. Interdum et malesuada fames ac ante ipsum primis in faucibus. Nunc tincidunt hendrerit facilisis. 
        
        Quisque eu sapien interdum, tempus dui non, tincidunt libero. Curabitur et auctor sem. Phasellus at massa quam. Vestibulum 
        volutpat lorem erat, ut varius leo sagittis nec. Vestibulum ut viverra ipsum. Donec semper quis lacus ac interdum. Vestibulum 
        non pellentesque mi, sed porttitor augue. Nam in nunc et nibh commodo eleifend. Proin ac vehicula orci, eu auctor tellus. 
        Nam fringilla hendrerit metus in sodales. Nam quis tempus nisi, nec aliquam lacus. Sed dictum mattis libero nec molestie. 
        Proin vel eleifend magna, ac efficitur magna. 
        """,
        1),
        
        ("How to apply this knowledge in the classroom",
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur sollicitudin nec lectus non malesuada. Fusce imperdiet odio ut 
        molestie volutpat. Ut nisi elit, semper sodales fermentum cursus, ullamcorper a sapien. Pellentesque dictum, turpis a varius 
        ultrices, nibh elit finibus metus, vel blandit risus diam non leo. Maecenas sagittis risus in massa faucibus euismod. Vivamus 
        faucibus vulputate dolor eget iaculis. Sed finibus felis non luctus lobortis. Sed porttitor ipsum ante, in sagittis nulla egestas 
        vitae. Mauris sed venenatis diam. Vivamus efficitur justo nisi, et tempor est egestas at. 
        
        Donec iaculis magna at magna sollicitudin scelerisque. Aenean id tortor vitae nisl lobortis consectetur at quis ipsum. Suspendisse 
        pulvinar mauris et sollicitudin ultricies. Aliquam eu odio ultricies, suscipit turpis in, interdum diam. Praesent ullamcorper luctus 
        tempus. Proin ligula odio, feugiat ac dolor sit amet, eleifend luctus nisi. In placerat, lacus et mattis tincidunt, nibh elit tristique 
        ante, eget tincidunt nunc tellus a neque. Duis at arcu in ligula convallis auctor. Ut eu risus tincidunt, blandit libero ut, luctus 
        nibh. Maecenas commodo blandit orci nec posuere. Duis venenatis quam eget eros convallis vulputate. Donec tincidunt nec urna 
        vel dictum. In et neque quam. Donec quis risus felis. Sed laoreet purus at metus lacinia iaculis.

        Ut sit amet nibh lacus. Mauris ac fermentum mauris. In ut consectetur ante. Ut pharetra tristique turpis vitae rhoncus. Vivamus 
        feugiat, augue bibendum elementum pretium, est sem pretium leo, ac accumsan arcu risus in tellus. Sed mollis laoreet metus, 
        nec aliquet felis aliquam quis. Aliquam at lacinia libero.

        Phasellus molestie risus fermentum vehicula pharetra. Proin hendrerit tristique erat, ut sollicitudin nulla ullamcorper ac. Integer 
        id pulvinar dui. Sed hendrerit fermentum turpis, eu vestibulum ipsum luctus vitae. Maecenas nec orci tempor, ultrices massa 
        vel, dapibus lorem. Nunc accumsan leo ipsum, nec volutpat ipsum malesuada id. Mauris sollicitudin leo eu tellus suscipit, nec 
        mollis risus pellentesque. Aenean lobortis ultricies ipsum, vitae tincidunt augue vehicula nec. Etiam mollis nunc ut risus blandit, 
        id faucibus tellus semper. Aliquam nec velit sodales, rutrum ex fermentum, eleifend ipsum.

        Aenean scelerisque nulla sollicitudin eros accumsan faucibus. Cras ac mi diam. Aenean tincidunt, nunc id condimentum luctus, 
        augue nisl convallis dui, suscipit faucibus sapien nunc id quam. Suspendisse pellentesque odio lobortis sapien volutpat, at 
        rhoncus ex convallis. Donec et arcu interdum, tincidunt est nec, interdum lorem. Nunc tristique magna ultrices elit vulputate
        lobortis in non quam. Cras consectetur ornare lectus id mollis. Cras odio tortor, feugiat at nibh eu, bibendum vestibulum velit. 
        Aliquam ultricies lectus sed dignissim iaculis. Morbi malesuada non velit in euismod. Praesent tincidunt odio risus, non viverra 
        erat lobortis in. Aenean posuere, odio at congue vestibulum, dui augue auctor nunc, vitae venenatis nisi mi rutrum velit. 
        Mauris faucibus nunc mattis, interdum metus quis, feugiat orci. Etiam fringilla nibh vitae lorem commodo, ac lobortis lacus 
        eleifend. 
        """,
        2),
]

TFquestions = [
        ("Is it true that you can take all the courses?", "Yes, you can take as many courses as you want."),
        ("Can you modify your own profile?", "Yes, the profile is modifiable in the Profile page."),
]

MCquestions = [
        ("Where can you find more information about Crichton Carbon Centre?",
         "The information about Crichton Carbon Centre can be found on the About page",
         [("On the About page", "Correct"), ("On the Forum", "False"), ("On the Dashboard", "False")]),

        ("What is the purpose of this platform?",
         "The purpose of this site is to learn about sustainability",
        [("To learn about sustainability", "Correct"),
         ("To learn about economy", "False"),
         ("To learn about statistics", "False")]),
]

question_options = [
        ("On the About page", "On the Forum", "On the Dashboard"),
        ("To learn about sustainability", "To learn about economy", "To learn about statistics"),
]

if __name__ == "__main__":
    # Clean DB just in case (optional)
    Page.objects.all().delete()
    Takers.objects.all().delete()
    Module.objects.all().delete()
    Teacher.objects.all().delete()
    User.objects.all().delete()
    Quiz.objects.all().delete()
    TF_Question.objects.all().delete()
    MCQuestion.objects.all().delete()
    Answer.objects.all().delete()
    Question.objects.all().delete()

    i = 0
    
    # ------ Teachers -------
    for name in names:
        # all dummy passwords are 123
        u = User.objects.create_user(name[0], 'smth@gmail.com', '123')
        
        u.first_name = name[1]
        u.last_name = name[2]
        u.save()
        
        # Make teachers
        Teacher.objects.get_or_create(user=u, bio=bios[i], school=schools[i])
        
        i+=1
        
    # ------ Modules -------
    for title in module_titles:
        # All modules have the same dummy text files
        m = Module(title=title)
        m.save()
        ContentFile.objects.create(module=m, file = File(open('downloadable_dummy.txt')))
        
        # Add takers
        # 3 attempts (pseudo randomness)
        for j in range(0,2):
            # fetch random user
            u = User.objects.order_by('?').first()
            # add to takers if not already present
            junc = Takers.objects.get_or_create(user=u, module=m)
            junc[0].progress = random.randint(0, 100)
            junc[0].save()
            
        # NOTE: Module.taker points to Manager object
        
    # ------- Pages ---------
    for module_entry in Module.objects.all():
        # add the random pages
        # NOTE: could be the same
        page_pos = 0
        for page in page_contents:
            Page.objects.get_or_create(module=module_entry,
                                                    section=page[0], 
                                                    content=page[1],
                                                    position=page[2])
   
    # ------- Quiz ---------
    for module_title in module_titles:
        q = Quiz.objects.create(title=module_title,
                                description="The purpose of this quiz is to test your knowledge about module: {:s}.".format(module_title),
                                module=Module.objects.get(title=module_title),
                                random_order=True,
                                exam_paper=True,
                                single_attempt=False,
                                success_text="Congratulations on passing the quiz!")
        for tf in TFquestions:
            question = Question.objects.create(content=tf[0], explanation=tf[1])
            question.quiz.add(q)
            question.save()
            question_tf = TF_Question.objects.create(question_ptr=question, correct=True)
            question_tf.__dict__.update(question.__dict__)
            question_tf.save()
        for mc in MCquestions:
            question = Question.objects.create(content=mc[0], explanation=mc[1])
            question.quiz.add(q)
            question.save()
            question_mc = MCQuestion.objects.create(question_ptr=question, answer_order="random")
            question_mc.__dict__.update(question.__dict__)
            question_mc.save()
            for ans in mc[2]:
                if ans[1] == "Correct":
                    answer = Answer.objects.get_or_create(question=question_mc, content=ans[0], correct=True)
                else:
                    answer = Answer.objects.get_or_create(question=question_mc, content=ans[0], correct=False)
