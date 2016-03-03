from django import forms
from django.utils.translation import ugettext_lazy as _


class TmlModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return _(super(TmlModelChoiceField, self).label_from_instance(obj))
