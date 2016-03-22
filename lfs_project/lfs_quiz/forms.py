from django import forms
from django.forms.models import inlineformset_factory
from .models import Quiz, TF_Question, MCQuestion, Answer
from django.forms.widgets import RadioSelect


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choice_list = [x for x in question.get_answers_list()]
        self.fields["answers"] = forms.ChoiceField(choices=choice_list,
                                                   widget=RadioSelect)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = ('module', 'draft',)


class MCQuestionForm(forms.ModelForm):

    class Meta:
        model = MCQuestion
        fields = ('content', 'module',
                  'figure', 'explanation', 'answer_order')


class TFQuestionForm(forms.ModelForm):
    class Meta:
        model = TF_Question
        fields = ('content', 'module',
                  'figure', 'explanation', 'correct',)


AnswerFormSet = inlineformset_factory(MCQuestion, Answer, exclude=('question', 'id'))
