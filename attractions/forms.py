from socket import fromshare
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models.outings import Outing

class OutingForm(forms.ModelForm):
    class Meta:
        model = Outing
        fields = ["start_time"]

    def __init__(self, *args, **kwargs):
        super(OutingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create"))