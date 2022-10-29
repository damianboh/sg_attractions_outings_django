from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_registration.forms import RegistrationForm as DefaultRegistrationForm

from .models import User

# custom registration form for user as we used email to log in
class RegistrationForm(DefaultRegistrationForm):
    class Meta(DefaultRegistrationForm.Meta):
        model = User
        fields = ["name", "email"]
    # add a submit button
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Register"))
