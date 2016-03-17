# encoding: UTF-8
from json import dumps, loads
from datetime import date, timedelta
from django.http import HttpResponse
from django.views.generic import TemplateView
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django_tml import tr, activate, activate_source, deactivate_source
from django_tml.translator import Translation
from tml.translation import TranslationOption
from tml.strings import to_string
from tml.decoration.parser import parse as decoration_parser


def get_translation(label, data, description, locale):
    activate(locale, dry_run=True)
    language = Translation.instance().context.language
    option = TranslationOption(label, language)
    return decoration_parser(option.execute(data, options={})).render(data)

@csrf_exempt
def translate(request):
    if not request.method.lower() == "post":
        return HttpResponse()
    label = request.POST.get('tml_label')
    data = loads(request.POST.get('tml_tokens') or "{}")
    description = request.POST.get('tml_context')
    locale = request.POST.get('tml_locale')
    trans_value = get_translation(label, data, description, locale)
    return HttpResponse(trans_value)


class IndexView(TemplateView):
    template_name = 'docs/index.html'


class DocsView(TemplateView):
    template_name = 'docs/docs.html'

    def get_context_data(self, * args, **kwargs):
        users = {
            'michael': User(to_string("Миша"), User.MALE),
            'alex': User("Alex", User.MALE),
            'anna': User(to_string("Анна"), User.FEMALE),
            'jenny': User("Jenny", User.FEMALE),
            'peter': User(to_string("Петр"), User.MALE),
            'karen': User("Karen", User.FEMALE),
            'thomas': User("Thomas", User.MALE),
        }
        kwargs.update({
            'users': users,
            'user_list': users.values(),
            'ten': xrange(1, 10),
            'five': xrange(1, 5),
            'dates': [
                date.today(),
                date.today() - timedelta(days=1),
                date.today() + timedelta(days=1)],
            'current_date': date.today()
        })
        return super(DocsView, self).get_context_data(**kwargs)


class ConsoleView(TemplateView):
    template_name = 'docs/docs.html'

class DummyView(TemplateView):
    template_name = 'docs/dummy.html'

    def get_context_data(self, *args, **kwargs):
        users = {
            'michael': User(to_string("Миша"), User.MALE),
            'alex': User("Alex", User.MALE),
            'anna': User(to_string("Анна"), User.FEMALE),
            'jenny': User("Jenny", User.FEMALE),
            'peter': User(to_string("Петр"), User.MALE),
            'karen': User("Karen", User.FEMALE),
            'thomas': User("Thomas", User.MALE),
        }
        kwargs.update({
            'users': users,
            'user_list': users.values(),
            'ten': xrange(1, 10),
            'five': xrange(1, 5),
            'dates': [
                date.today(),
                date.today() - timedelta(days=1),
                date.today() + timedelta(days=1)],
            'current_date': date.today()
        })
        return super(DummyView, self).get_context_data(**kwargs)
