from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models.outings import Outing, OutingInvitation, Comment
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

UserModel = get_user_model()

# To create outings
class OutingForm(forms.ModelForm):
    class Meta:
        model = Outing
        fields = ["start_time"]

    def __init__(self, *args, **kwargs):
        super(OutingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create"))
        
    def clean_start_time(self):
        start_time = self.cleaned_data["start_time"]
        if start_time < timezone.now():
            raise ValidationError(
                _("Unable to create outing as start time is in the past."), 
                    code='invalid'
                )
        
        return start_time

# To invite users to outings via their email
class InviteeForm(forms.Form):
    email = forms.EmailField()
    _user = False

    # invitee form not tagged to OutingInvite object as email is used to invite
    # get user profile from email then create OutingInvite instance manually in views
    def __init__(self, *args, **kwargs):
        super(InviteeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit_invite", "Invite"))

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            # cache for later
            self._userProfile = UserModel.objects.get(email=email).profile
        except UserModel.DoesNotExist:
            # only can invite users who have signed up in the website
            raise ValidationError(
                _("User with email address '%(email)s' was not found."), 
                    code='invalid', 
                params={'email':email}
                )
        
        return email


# To mark whether user is attending
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = OutingInvitation
        fields = ["is_attending"]

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields["is_attending"].label = "Attending?"
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Update Attendance"))


# To comment on outings
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit_comment", "Add Comment"))
