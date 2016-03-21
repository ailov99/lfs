from __future__ import unicode_literals
import re
import json

from django.db import models
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MaxValueValidator
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings

from model_utils.managers import InheritanceManager

from lfs.models import Module

ANSWER_ORDER_OPTIONS = (
    ('content', 'Content'),
    ('random', 'Random'),
    ('none', 'None')
)

@python_2_unicode_compatible
class Quiz(models.Model):
    title = models.CharField(
            verbose_name="Title",
            max_length=60, blank=False)

    description = models.TextField(
            verbose_name="Description",
            blank=True, help_text="a description of the quiz")

    module = models.OneToOneField(
            Module, null=True, blank=False,
            verbose_name="Module")

    random_order = models.BooleanField(
            blank=False, default=False,
            verbose_name="Random Order",
            help_text="Display the questions in "
                        "a random order or as they "
                        "are set?")

    max_questions = models.PositiveIntegerField(
            blank=True, null=True, verbose_name="Max Questions",
            help_text="Number of questions to be answered on each attempt.")

    exam_paper = models.BooleanField(
            blank=False, default=True,
            help_text="If yes, the result of each"
                        " attempt by a user will be"
                        " stored.",
            verbose_name="Exam Paper")

    single_attempt = models.BooleanField(
            blank=False, default=False,
            help_text="If yes, only one attempt by"
                        " a user will be permitted.",
            verbose_name="Single Attempt")

    pass_mark = models.SmallIntegerField(
            blank=True, default=0,
            help_text="Percentage required to pass exam.",
            validators=[MaxValueValidator(100)])

    success_text = models.TextField(
            blank=True, help_text="Displayed if user passes.",
            verbose_name="Success Text")

    fail_text = models.TextField(
            verbose_name="Fail Text",
            blank=True, help_text="Displayed if user fails.")

    draft = models.BooleanField(
            blank=True, default=False,
            verbose_name="Draft",
            help_text="If yes, the quiz is not displayed"
                        " in the quiz list and can only be"
                        " taken by users who can edit"
                        " quizzes.")

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # self.url = re.sub('\s+', '-', self.url).lower()
        #
        # self.url = ''.join(letter for letter in self.url if
        #                    letter.isalnum() or letter == '-')

        if self.single_attempt is True:
            self.exam_paper = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def anon_score_id(self):
        return str(self.id) + "_score"

    def anon_q_list(self):
        return str(self.id) + "_q_list"

    def anon_q_data(self):
        return str(self.id) + "_data"


class ProgressManager(models.Manager):
    def new_progress(self, user):
        new_progress = self.create(user=user,
                                   score="")
        new_progress.save()
        return new_progress


class Progress(models.Model):
    """
    Progress is used to track an individual signed in users score on different
    quiz's and categories

    Data stored in csv using the format:
        category, score, possible, category, score, possible, ...
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="User")

    score = models.CommaSeparatedIntegerField(max_length=1024,
                                              verbose_name="Score")

    objects = ProgressManager()

    class Meta:
        verbose_name = "User Progress"
        verbose_name_plural = "User progress records"

    @property
    def list_all_mod_scores(self):
        """
        Returns a dict in which the key is the module name and the item is
        a list of three integers.

        The first is the number of questions correct,
        the second is the possible best score,
        the third is the percentage correct.

        The dict will have one key for every module that you have defined
        """
        score_before = self.score
        output = {}

        for mod in Module.objects.all():
            to_find = re.escape(mod.title) + r",(\d+),(\d+),"
            #  group 1 is score, group 2 is highest possible

            match = re.search(to_find, self.score, re.IGNORECASE)

            if match:
                score = int(match.group(1))
                possible = int(match.group(2))

                try:
                    percent = int(round((float(score) / float(possible))
                                        * 100))
                except:
                    percent = 0

                output[mod.title] = [score, possible, percent]

            else:  # if category has not been added yet, add it.
                self.score += mod.title + ",0,0,"
                output[mod.title] = [0, 0]

        if len(self.score) > len(score_before):
            # If a new category has been added, save changes.
            self.save()

        return output

    def update_score(self, question, score_to_add=0, possible_to_add=0):
        """
        Pass in question object, amount to increase score
        and max possible.

        Does not return anything.
        """
        module_test = Module.objects.filter(title=question.module) \
            .exists()

        if any([item is False for item in [module_test,
                                           score_to_add,
                                           possible_to_add,
                                           isinstance(score_to_add, int),
                                           isinstance(possible_to_add, int)]]):
            return "error", "category does not exist or invalid score"

        to_find = re.escape(str(question.module)) + \
                  r",(?P<score>\d+),(?P<possible>\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            updated_score = int(match.group('score')) + abs(score_to_add)
            updated_possible = int(match.group('possible')) + \
                               abs(possible_to_add)

            new_score = ",".join(
                    [
                        str(question.module),
                        str(updated_score),
                        str(updated_possible), ""
                    ])

            # swap old score for the new one
            self.score = self.score.replace(match.group(), new_score)
            self.save()

        else:
            #  if not present but existing, add with the points passed in
            self.score += ",".join(
                    [
                        str(question.module),
                        str(score_to_add),
                        str(possible_to_add),
                        ""
                    ])
            self.save()

    def show_exams(self):
        """
        Finds the previous quizzes marked as 'exam papers'.
        Returns a queryset of complete exams.
        """
        return Sitting.objects.filter(user=self.user, complete=True)


class SittingManager(models.Manager):
    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = quiz.question_set.all() \
                .order_by('?')
        else:
            question_set = quiz.question_set.all()

        question_ids = question_set.values_list('id', flat=True)

        if question_set.count() == 0:
            raise ImproperlyConfigured('Question set of the quiz is empty. '
                                       'Please configure questions properly')

        if quiz.max_questions and quiz.max_questions < question_set.count():
            question_ids = question_ids[:quiz.max_questions]

        questions = ",".join(map(str, question_ids)) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  question_list=questions,
                                  incorrect_questions="",
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}')
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.single_attempt is True and self.filter(user=user,
                                                       quiz=quiz,
                                                       complete=True) \
                .exists():
            return False

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False)[0]
        return sitting


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting a quiz.
    Replaces the session system used by anon users.

    Question_order is a list of integer pks of all the questions in the
    quiz, in order.

    Question_list is a list of integers which represent id's of
    the unanswered questions in csv format.

    Incorrect_questions is a list in the same format.

    Sitting deleted when quiz finished unless quiz.exam_paper is true.

    User_answers is a json object in which the question PK is stored
    with the answer the user gave.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User")

    quiz = models.ForeignKey(Quiz, verbose_name="Quiz")

    question_order = models.CommaSeparatedIntegerField(
            max_length=1024, verbose_name="Question Order")

    question_list = models.CommaSeparatedIntegerField(
            max_length=1024, verbose_name="Question List")

    incorrect_questions = models.CommaSeparatedIntegerField(
            max_length=1024, blank=True, verbose_name="Incorrect questions")

    current_score = models.IntegerField(verbose_name="Current Score")

    complete = models.BooleanField(default=False, blank=False,
                                   verbose_name="Complete")

    user_answers = models.TextField(blank=True, default='{}',
                                    verbose_name="User Answers")

    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name="Start")

    end = models.DateTimeField(null=True, blank=True, verbose_name="End")

    objects = SittingManager()

    class Meta:
        permissions = (("view_sittings", "Can see completed exams."),)

    def get_first_question(self):
        """
        Returns the next question.
        If no question is found, returns False
        Does NOT remove the question from the front of the list.
        """
        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids())
        if divisor < 1:
            return 0  # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    def add_incorrect_question(self, question):
        """
        Adds uid of incorrect question to the list.
        The question object must be passed in.
        """
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        """
        Returns a list of non empty integers, representing the pk of
        questions
        """
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.quiz.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.quiz.success_text
        else:
            return self.quiz.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
                self.quiz.question_set.filter(id__in=question_ids)
                    .select_subclasses(),
                key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]

        return questions

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
            }

    @property
    def get_max_score(self):
        return len(self._question_ids())

    def progress(self):
        """
        Returns the number of questions answered so far and the total number of
        questions.
        """
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total


@python_2_unicode_compatible
class Question(models.Model):
    """
    Base class for all question types.
    Shared properties placed here.
    """

    quiz = models.ManyToManyField(Quiz,
                                  verbose_name="Quiz",
                                  blank=True)

    module = models.ForeignKey(Module,
                                 verbose_name="Module",
                                 blank=True,
                                 null=True)

    figure = models.ImageField(upload_to='static/quiz',
                               blank=True,
                               null=True,
                               verbose_name="Figure")

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text="Enter the question text that "
                                           "you want displayed",
                               verbose_name='Question')

    explanation = models.TextField(max_length=2000,
                                   blank=True,
                                   help_text="Explanation to be shown "
                                               "after the question has "
                                               "been answered.",
                                   verbose_name='Explanation')

    objects = InheritanceManager()

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['module']

    def __str__(self):
        return str(self.content)


class MCQuestion(Question):
    answer_order = models.CharField(
            max_length=30, null=True, blank=True,
            choices=ANSWER_ORDER_OPTIONS,
            help_text="The order in which multichoice "
                      "answer options are displayed "
                      "to the user",
            verbose_name="Answer Order")

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


@python_2_unicode_compatible
class Answer(models.Model):
    question = models.ForeignKey(MCQuestion, verbose_name="Question")

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text="Enter the answer text that "
                                         "you want displayed",
                               verbose_name="Content")

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Is this a correct answer?",
                                  verbose_name="Correct")

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"


class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Tick this if the question "
                                              "is true. Leave it blank for"
                                              " false.",
                                  verbose_name="Correct")

    def check_if_correct(self, guess):
        if guess == "True":
            guess_bool = True
        elif guess == "False":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct("True"),
                 'content': 'True'},
                {'correct': self.check_if_correct("False"),
                 'content': 'False'}]

    def get_answers_list(self):
        return [(True, True), (False, False)]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = "True/False Question"
        verbose_name_plural = "True/False Questions"
        ordering = ['module']