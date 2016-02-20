from __future__ import absolute_import
# encoding: UTF-8
from django.test import SimpleTestCase
from .translator import Translator
from gettext import ngettext, gettext
from django.template import Template
from django.template.context import Context
from django_tml import activate, activate_source, inline_translations, tr,\
    deactivate_source
from tml.tools.viewing_user import set_viewing_user
from copy import copy
from django.conf import settings
from os.path import dirname
from tml.api.mock import Hashtable as DumbClient
from tml.context import SourceContext
from tml.exceptions import Error
from tml.decoration import AttributeIsNotSet
from tml.translation import Key
from tml.strings import to_string
import six

class WithSnapshotSettings(object):
    def __init__(self):
        self.TML = {}
        for key in settings.TML:
            self.TML[key] = settings.TML[key]
        self.TML['snapshot'] = dirname(settings.FIXTURES_PATH) + '/snapshot.tar.gz'


class DjangoTMLTestCase(SimpleTestCase):
    """ Tests for django tml tranlator """
    def setUp(self):
        Translator._instance = None # reset settings
        inline_translations.turn_off()

    def test_tranlator(self):
        t = Translator.instance()
        self.assertEquals(Translator, t.__class__, "Instance returns translator")
        self.assertEquals(t, Translator.instance(), "Singletone")

    def test_languages(self):
        """ Language switch """
        t = Translator.instance()
        # reset en tranlation:
        en_hello_url = t.client.build_url('translation_keys/90e0ac08b178550f6513762fa892a0ca/translations',
                                          {'locale':'en', 'page': 1})
        t.client.data[en_hello_url] = {'error':'Force error'}
        self.assertEquals(['en', 'id', 'ru'], t.supported_locales)
        self.assertEquals('en', t.get_language(), 'Use default language if not set')
        self.assertEqual(to_string('Hello John'), t.tr('Hello {name}', {'name':'John'}), 'Use fallback tranlation')
        t.activate('ru')
        self.assertEquals('ru', t.get_language(), 'Set custom language')
        self.assertEqual(to_string('Привет John'), t.tr('Hello {name}', {'name':'John'}), 'Fetch tranlation')
        t.activate('de')
        self.assertEquals('en', t.get_language(), 'If language is not supported reset to default')
        t.activate('id')
        self.assertEquals('id', t.get_language(), 'All supported languages is works')
        t.deactivate_all()
        self.assertEquals('en', t.get_language(), 'Deactivate all')

    def test_source(self):
        """ Test languages source """
        t = Translator.instance()
        t.activate('ru')
        t.activate_source('index')
        self.assertEqual(to_string('Привет John'), t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')
        t.activate_source('alpha')
        self.assertEqual(to_string('Hello John'), t.tr('Hello {name}', {'name':'John'}), 'Use fallback translation')
        # flush missed keys on change context:
        client = t.context.language.client
        t.activate_source('index')
        self.assertEquals('sources/register_keys', client.url, 'Flush missed keys')
        # handle change:
        self.assertEqual(to_string('Привет John'), t.tr('Hello {name}', {'name':'John'}), 'Fetch translation')

    def test_gettext(self):
        t = Translator.instance()
        t.activate('ru')
        t.activate_source('index')
        self.assertEqual(to_string('Привет %(name)s'), t.ugettext('Hello {name}'), 'ugettext')
        gettext_result = t.gettext('Hello {name}')
        self.assertEqual(to_string('Привет %(name)s'), to_string(gettext_result), 'gettext content')
        self.assertEqual(six.text_type, type(gettext_result),'gettext returns str')
        pgettext_result = t.pgettext('Greeting', 'Hi {name}')
        self.assertEqual(to_string('Здорово %(name)s'), to_string(pgettext_result), 'ugettext')
        self.assertEqual(six.text_type, type(pgettext_result),'pgettext returns str')
        self.assertEquals(to_string('Одно яблоко'), t.ungettext('One apple', '{number} apples', 1), 'ungettext + 1')
        self.assertEquals(to_string('Одно яблоко'), to_string(t.ngettext('One apple', '{number} apples', 1)), 'ngettext + 1')
        self.assertEquals(six.text_type, type(t.ngettext('One apple', '{number} apples', 1)), 'ngettext type')
        self.assertEquals(to_string('%(number)s яблоко'), t.ungettext('One apple', '{number} apples', 21), 'ungettext + 21')
        self.assertEquals(to_string('%(number)s яблока'), t.ungettext('One apple', '{number} apples', 22), 'ungettext + 22')
        self.assertEquals(to_string('%(number)s яблок'), t.ungettext('One apple', '{number} apples', 5), 'ungettext + 5')
        self.assertEquals(to_string('%(number)s яблок'), to_string(t.ngettext('One apple', '{number} apples', 12)), 'ngettext + 12')

    def test_format_attributes(self):
        t = Template('{% load tml %}{% tr %}[link]Hello[/link]{% endtr %}')
        self.assertEquals('<a href="url">Hello</a>', t.render(Context({'link_href':'url'})), 'Test format attributes')
        self.assertEquals('<a href="url">Hello</a>', t.render(Context({'link':'url'})), 'Test format attributes')
        self.assertEquals('<a href="url">Hello</a>', t.render(Context({'link':{'href':'url'}})), 'Test format attributes')
        with self.assertRaises(Error) as context:
            t.render(Context({}))

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
        self.assertEquals(to_string('Привет John'), t.render(c))
        t = Template(
        '''
        {%load tml %}
        {% tr trimmed %}
            Hello {name}
        {% endtr %}
        ''')
        self.assertEquals(to_string('''Привет John'''), t.render(c).strip(), 'Trimmed support')
        t = Template(to_string('{%load tml %}{% tr with name="Вася" %}Hello {name}{% endtr %}'))
        self.assertEquals(to_string('Привет Вася'), t.render(c), 'With syntax')

        t = Template('{%load tml %}{% tr %}Hello {name}{% endtr %}')
        self.assertEquals(to_string('Привет &lt;&quot;Вася&quot;&gt;'), t.render(Context({'name':'<"Вася">'})))
        t = Template(to_string('{%load tml %}{% tr with html|safe as name %}Hello {name}{% endtr %}'))
        self.assertEquals(to_string('Привет <"Вася">'), t.render(Context({'html':'<"Вася">'})))

    def test_blocktrans(self):
        activate('ru')
        activate_source('blocktrans')
        c = Context({'name':'John'})

        t = Template('{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}')
        self.assertEquals(to_string('Привет John'), t.render(c))

        t = Template('{%load tml %}{% blocktrans %}Hello {{name}}{% endblocktrans %}')
        self.assertEquals(to_string('Привет John'), t.render(c), 'Use new tranlation')

        t = Template('{%load tml %}{% blocktrans %}Hey {{name}}{% endblocktrans %}') 
        self.assertEquals(to_string('Эй John, привет John'), t.render(c), 'Use old tranlation')

        t = Template('{%load tml %}{% blocktrans count count=apples_count %}One apple{% plural %}{count} apples{% endblocktrans %}')
        self.assertEquals(to_string('Одно яблоко'), t.render(Context({'apples_count':1})),'Plural one')
        self.assertEquals(to_string('2 яблока'), t.render(Context({'apples_count':2})),'Plural 2')
        self.assertEquals(to_string('21 яблоко'), t.render(Context({'apples_count':21})),'Plural 21')

    def test_inline(self):
        """ Inline tranlations wrapper """
        activate('ru')
        inline_translations.turn_on()
        c = Context({'name':'John'})
        t = Template(to_string('{%load tml %}{% tr %}Hello {name}{% endtr %}'))

        self.assertEquals(to_string('<tml:label class="tml_translatable tml_translated" data-translation_key="90e0ac08b178550f6513762fa892a0ca" data-target_locale="ru">Привет John</tml:label>'),
                          t.render(c),
                          'Wrap translation')
        t = Template(to_string('{%load tml %}{% tr nowrap %}Hello {name}{% endtr %}'))
        self.assertEquals(to_string('Привет John'),
                          t.render(c),
                          'Nowrap option')

        t = Template(to_string('{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}'))
        self.assertEquals(to_string('Привет John'),
                          t.render(c),
                          'Nowrap blocktrans')

        t = Template(to_string('{%load tml %}{% tr %}Untranslated{% endtr %}'))
        self.assertEquals(to_string('<tml:label class="tml_translatable tml_not_translated" data-translation_key="9bf6a924c9f25e53a6b07fc86783bb7d" data-target_locale="ru">Untranslated</tml:label>'),
                          t.render(c),
                          'Untranslated')
        activate('ru')
        inline_translations.turn_off()
        t = Template(to_string('{%load tml %}{% tr %}Hello {name}{% endtr %}'))
        t = Template(to_string('{%load tml %}{% blocktrans %}Hello {name}{% endblocktrans %}'))
        self.assertEquals(to_string('Привет John'),
                          t.render(c),
                          'Turn off inline')

    def test_sources_stack(self):
        t = Translator.instance()
        self.assertEqual(None, t.source, 'None source by default')
        t.activate_source('index')
        self.assertEqual('index', t.source, 'Use source')
        t.enter_source('auth')
        self.assertEqual('auth', t.source, 'Enter (1 level)')
        t.enter_source('mail')
        self.assertEqual('mail', t.source, 'Enter (2 level)')
        t.exit_source()
        self.assertEqual('auth', t.source, 'Exit (2 level)')
        t.exit_source()
        self.assertEqual('index', t.source, 'Exit (1 level)')
        t.exit_source()
        self.assertEqual(None, t.source, 'None source by default')

        t.activate_source('index')
        t.enter_source('auth')
        t.enter_source('mail')
        t.activate_source('inner')
        t.exit_source()
        self.assertEqual(None, t.source, 'Use destroys all sources stack')

    def test_preprocess_data(self):
        activate('ru')
        self.assertEquals(to_string('Привет Вася and Петя'), tr('Hello {name}', {'name':['Вася','Петя']}))
        t = Template(to_string('{%load tml %}{% tr %}Hello {name}{% endtr %}'))
        self.assertEquals(to_string('Привет Вася and Петя'), t.render(Context({'name':['Вася','Петя']})))

    def test_viewing_user(self):
        activate('ru')
        set_viewing_user({'name':'John','gender':'male'})
        deactivate_source()
        self.assertEquals('Mr', tr('honorific'))
        set_viewing_user('female')
        self.assertEquals('Ms', tr('honorific'))

    def test_snapshot_context(self):
        t = Translator(WithSnapshotSettings())
        self.assertTrue(t.use_snapshot, 'Use snapshot with settings')
        t.activate('ru')
        self.assertEquals('Test', t.context.tr('Test'), 'Stub translation without source')
        t.activate_source('xxxx')
        self.assertEquals(to_string('Тест'), t.context.tr('Test'), 'Works with source')
        t.activate_source('notexists')
        self.assertEquals(to_string('Test'), t.context.tr('Test'), 'Notexists source')

