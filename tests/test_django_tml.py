from __future__ import absolute_import, unicode_literals
# encoding: UTF-8
import six
from os.path import dirname
from copy import deepcopy
from django.conf import settings
from django.test import SimpleTestCase
from gettext import ngettext, gettext
from django.template import Template
from django.template.context import Context
from tml.api.mock import Hashtable as DumbClient
from tml.context import SourceContext
from tml.exceptions import Error
from tml.decoration import AttributeIsNotSet
from tml.translation import Key
#from tml.strings import unicode
from tml.tools.viewing_user import set_viewing_user
from django_tml import activate, activate_source, tr,\
    deactivate_source
from django_tml.translator import Translation

# encoding: UTF-8
__author__ = 'a@toukmanov.ru, xepa4ep'


def WithSnapshotSettings():
    TML = deepcopy(settings.TML)
    TML['cache'] = {
        'enabled': True,
        'adapter': 'file',
        'path': dirname(settings.FIXTURES_PATH) + '/snapshot.tar.gz'
    }
    TML['environment'] = 'test'
    return TML

def WithDefaultSettings():
    return settings.TML


class DjangoTMLTestCase(SimpleTestCase):
    """ Tests for django tml tranlator """
    def setUp(self):
        Translation._instance = None # reset settings
        Translation.instance(tml_settings=WithDefaultSettings())

    def test_tranlator(self):
        t = Translation.instance(tml_settings=WithDefaultSettings())
        self.assertEquals(Translation, t.__class__, "Instance returns translator")
        self.assertEquals(t, Translation.instance(), "Singletone")

    def test_languages(self):
        """ Language switch """
        t = Translation.instance(tml_settings=WithDefaultSettings())
        # reset en tranlation:
        en_hello_url = t.client.build_url('translation_keys/90e0ac08b178550f6513762fa892a0ca/translations',
                                          {'locale':'en'})
        t.client.data[en_hello_url] = {'error':'Force error'}
        self.assertEquals(['en', 'id', 'ru'], t.supported_locales)
        self.assertEquals('en', t.get_language(), 'Use default language if not set')
        self.assertEqual(unicode('Hello John'), t.tr('Hello {name}', {'name':'John'}))
        t.activate('ru')
        self.assertEquals('ru', t.get_language(), 'Set custom language')
        self.assertEqual(unicode('Привет John'), t.tr('Hello {name}', {'name':'John'}), 'Fetch tranlation')
        t.activate('de')
        self.assertEquals('en', t.get_language(), 'If language is not supported reset to default')
        t.activate('id')
        self.assertEquals('id', t.get_language(), 'All supported languages is works')
        t.deactivate_all()
        self.assertEquals('en', t.get_language(), 'Deactivate all')

    def test_source(self):
        """ Test languages source """
        t = Translation.instance(tml_settings=WithDefaultSettings())
        t.activate('ru')
        t.activate_source('index')
        self.assertEqual(unicode('Привет John'), t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')
        t.activate_source('alpha')
        self.assertEqual(unicode('Hello John'), t.tr('Hello {name}', {'name':'John'}), 'Use fallback translation')
        # flush missed keys on change context:
        client = t.context.language.client
        t.activate_source('index')
        self.assertEquals('sources/register_keys', client.url, 'Flush missed keys')
        # handle change:
        self.assertEqual(unicode('Привет John'), t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')

    def test_gettext(self):
        t = Translation.instance(tml_settings=WithDefaultSettings())
        t.activate('ru')
        t.activate_source('index')
        self.assertEqual(unicode('Привет %(name)s'), t.ugettext('Hello {name}'), 'ugettext')
        gettext_result = t.gettext('Hello {name}')
        self.assertEqual(unicode('Привет %(name)s'), unicode(gettext_result), 'gettext content')
        self.assertEqual(six.text_type, type(gettext_result),'gettext returns str')
        pgettext_result = t.pgettext('Greeting', 'Hi {name}')
        self.assertEqual(unicode('Здорово %(name)s'), unicode(pgettext_result), 'ugettext')
        self.assertEqual(six.text_type, type(pgettext_result),'pgettext returns str')
        self.assertEquals(unicode('Одно яблоко'), t.ungettext('One apple', '{number} apples', 1), 'ungettext + 1')
        self.assertEquals(unicode('Одно яблоко'), unicode(t.ngettext('One apple', '{number} apples', 1)), 'ngettext + 1')
        self.assertEquals(six.text_type, type(t.ngettext('One apple', '{number} apples', 1)), 'ngettext type')
        self.assertEquals(unicode('%(number)s яблоко'), t.ungettext('One apple', '{number} apples', 21), 'ungettext + 21')
        self.assertEquals(unicode('%(number)s яблока'), t.ungettext('One apple', '{number} apples', 22), 'ungettext + 22')
        self.assertEquals(unicode('%(number)s яблок'), t.ungettext('One apple', '{number} apples', 5), 'ungettext + 5')
        self.assertEquals(unicode('%(number)s яблок'), unicode(t.ngettext('One apple', '{number} apples', 12)), 'ngettext + 12')

    def test_format_attributes(self):
        t = Template('{% load tml %}{% tr %}[link]Hello[/link]{% endtr %}')
        self.assertEquals('<a href="url">Hello</a>', t.render(Context({'link_href':'url'})), 'Test format attributes')
        self.assertEquals('<a href="url">Hello</a>', t.render(Context({'link':'url'})), 'Test format attributes')
        self.assertEquals('<a href="url">Hello</a>', t.render(Context({'link':{'href':'url'}})), 'Test format attributes')

    def test_default_language(self):
        activate('ru')
        self.assertEquals('1 banana', tr('{count||banana,bananas}', {'count': 1}, 'Use default language in fallback'))
        t = Template('{% load tml %}{% tr %}{count||apple,apples}{% endtr %}')
        self.assertEquals('2 apples', t.render(Context({'count':2})), 'Render fallback with default language')


    def test_template_tags(self):
        """ Test for template tags """
        activate('ru')
        t = Template('{%load tml %}{% tr %}Hello {name}{% endtr %}')
        c = Context({'name':'John'})
        self.assertEquals(unicode('Привет John'), t.render(c))
        t = Template(
        '''
        {%load tml %}
        {% tr trimmed %}
            Hello {name}
        {% endtr %}
        ''')
        self.assertEquals(unicode('''Привет John'''), t.render(c).strip(), 'Trimmed support')
        t = Template(unicode('{%load tml %}{% tr with name="Вася" %}Hello {name}{% endtr %}'))
        self.assertEquals(unicode('Привет Вася'), t.render(c), 'With syntax')

        t = Template('{%load tml %}{% tr %}Hello {name}{% endtr %}')
        self.assertEquals(unicode('Привет &lt;&quot;Вася&quot;&gt;'), t.render(Context({'name':'<"Вася">'})))
        t = Template(unicode('{%load tml %}{% tr with html|safe as name %}Hello {name}{% endtr %}'))
        self.assertEquals(unicode('Привет <"Вася">'), t.render(Context({'html':'<"Вася">'})))

        Translation.instance().activate_source('index')
        t = Template('{% load tml %}{% tmlopts with source="navigation" %}{% trs "hello world" %}{% endtmlopts %}')
        rv = t.render(Context({}))
        self.assertEquals(rv, 'hello world')

        Translation.instance().activate_source('index')
        t = Template('{% load tml %}{% tmlopts with source=navigation %}{% tr %}Hello {name}{% endtr %}{% endtmlopts %}')
        rv = t.render(Context({'navigation': 'nav', 'name': 'Вася'}))
        self.assertEquals(rv, 'Привет Вася')

        Translation.instance().activate_source('index')
        t = Template('{% load tml %}{% tmlopts with source=navigation %}{% tmlopts with source=basic %}{% tr %}Hello {name}{% endtr %}{% endtmlopts %}{% endtmlopts %}')
        rv = t.render(Context({'navigation': 'nav', 'basic': 'base', 'name': 'Вася'}))
        self.assertEquals(rv, 'Привет Вася')
        Translation.instance().deactivate_source()

    def test_blocktrans(self):
        activate('ru')
        activate_source('blocktrans')
        c = Context({'name':'John'})

        t = Template('{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}')
        self.assertEquals(unicode('Привет John'), t.render(c))

        t = Template('{%load tml %}{% blocktrans %}Hello {{name}}{% endblocktrans %}')
        self.assertEquals(unicode('Привет John'), t.render(c), 'Use new tranlation')

        # t = Template('{%load tml %}{% blocktrans %}Hey {{name}}{% endblocktrans %}')
        # self.assertEquals(unicode('Эй John, привет John'), t.render(c), 'Use old tranlation')

        t = Template('{%load tml %}{% blocktrans count count=apples_count %}One apple{% plural %}{count} apples{% endblocktrans %}')
        self.assertEquals(unicode('Одно яблоко'), t.render(Context({'apples_count':1})),'Plural one')
        self.assertEquals(unicode('2 яблока'), t.render(Context({'apples_count':2})),'Plural 2')
        self.assertEquals(unicode('21 яблоко'), t.render(Context({'apples_count':21})),'Plural 21')

    # def test_sources_stack(self):
    #     t = Translation.instance(tml_settings=WithDefaultSettings())
    #     self.assertEqual(None, t.source, 'None source by default')
    #     t.activate_source('index')
    #     self.assertEqual('index', t.source, 'Use source')
    #     t.enter_source('auth')
    #     self.assertEqual('auth', t.source, 'Enter (1 level)')
    #     t.enter_source('mail')
    #     self.assertEqual('mail', t.source, 'Enter (2 level)')
    #     t.exit_source()
    #     self.assertEqual('auth', t.source, 'Exit (2 level)')
    #     t.exit_source()
    #     self.assertEqual('index', t.source, 'Exit (1 level)')
    #     t.exit_source()
    #     self.assertEqual(None, t.source, 'None source by default')

    #     t.activate_source('index')
    #     t.enter_source('auth')
    #     t.enter_source('mail')
    #     t.activate_source('inner')
    #     t.exit_source()
    #     self.assertEqual(None, t.source, 'Use destroys all sources stack')

    def test_preprocess_data(self):
        activate('ru')
        self.assertEquals(unicode('Привет Вася and Петя'), tr('Hello {name}', {'name':['Вася','Петя'], 'last_separator': 'and'}))
        t = Template(unicode('{%load tml %}{% tr %}Hello {name}{% endtr %}'))
        self.assertEquals(unicode('Привет Вася and Петя'), t.render(Context({'name':['Вася','Петя'], 'last_separator': 'and'})))

    def test_viewing_user(self):
        activate('ru')
        set_viewing_user({'name':'John','gender':'male'})
        deactivate_source()
        self.assertEquals('Mr', tr('honorific'))
        set_viewing_user('female')
        self.assertEquals('Ms', tr('honorific'))
