from django import forms
from django.urls import reverse
from django.utils.timezone import timedelta
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from ExCSystem.settings.base import WEB_BASE
from core.models import Member, Staffer
from core.convinience import get_all_rfids
from core.forms.fields.RFIDField import RFIDField


class MemberCreationForm(forms.ModelForm):
    """
    A form for creating new members. Includes all the required
    fields, plus a repeated password.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    username = forms.EmailField(label='Email')
    rfid = RFIDField(label='RFID')
    # membership_rfid = forms.CharField(label="Membership RFID", max_length=10, widget=forms.TextInput)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('username', 'rfid', 'password1', 'password2',)

    def clean_username(self):
        email = self.cleaned_data['username']
        # If a member exists with this email, raise a validation error
        current = Member.objects.filter(email=email)
        if current:
            raise forms.ValidationError("The email '{email}' is already in use!".format(email=email))
        return email

    def clean_rfid(self):
        rfid = self.cleaned_data['rfid']
        if len(rfid) != 10:
            raise forms.ValidationError("This is not a valid 10 digit RFID!")
        if rfid in get_all_rfids():
            raise forms.ValidationError("This RFID is already in use!")
        return rfid

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """
        Save the newly created member
        :param commit: This is ignored, we always commit
        """

        # We will always commit the save, so make sure m2m fields are always saved
        self.save_m2m = self._save_m2m

        email = self.cleaned_data['username']
        rfid = self.cleaned_data['rfid']
        password = self.cleaned_data['password1']
        duration = timedelta(days=90)
        member = Member.objects.create_member(email, rfid, duration, password)
        finish_url = WEB_BASE + reverse("admin:core_member_finish", kwargs={'pk': member.pk})
        member.send_intro_email(finish_url)
        return member


class MemberFinishForm(forms.ModelForm):
    """
    Form used to let the member finish their account setup

    To finish setting up their account, members must submit all missing data (ie phone number) and successfully complete
    a quiz about the rules of the club.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'phone_number', 'picture')


class MemberChangeRFIDForm(forms.ModelForm):
    """
    Form to expedite the process of changing a users RFID tag

    This form allows a member to replace a lost or missing RFID tag. Note: a member cannot have more than one RFID

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('rfid', )


class MemberChangeCertsForm(forms.ModelForm):
    """
    Form to add/remove certifications from the member

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('certifications', )


class MemberUpdateContactForm(forms.ModelForm):
    """
    Form to expedite the process of updating a members contact info (email, phone)

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('email', 'phone_number')


class MemberChangeGroupsForm(forms.ModelForm):
    """
    Form to change the status of a member, and dispatch any additional data requirements

    This form should only be accessible to users with high status (board or above) and allows them to change the status
    of the member in the system. Once the form is submitted further data processing is dispatched based on the change in
    status.
    Ex:
        If a Member becomes a staffer, then they are emailed a form with additional staffer information.
        If a Staffer is demoted, then their associated staff profile is removed.

    """

    class Meta:
        model = Member
        fields = ('group',)


class StafferDataForm(forms.ModelForm):
    """
    Form to request the additional information required when becoming a staffer.

    A link to this form should be emailed to a member when they are upgraded to a staffer, or when a staffer wishes to
    edit their description or other staff data.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    exc_email = forms.CharField(
        label="Staffer Nickname",
        max_length=20,
        help_text="The name of the staffer: to be used as the beginning of the email address"
    )

    class Meta:
        model = Staffer
        # Member should already be known when this form is accessed, so having it as a field is excessive
        fields = ('exc_email', 'autobiography')

    def clean_exc_email(self):
        """
        Although the field is named exc_email, the input should only be the staff name, so append rest of email here
        """
        staff_name = self.cleaned_data['exc_email']
        return staff_name + "@excursionclubucsb.org"


class MemberChangeForm(forms.ModelForm):
    """
    A form for changing members. Includes all fields, except password is hashed.

    This form can change pretty much anything about the member and exposes all the data. Therefore it should only be
    used in unexpected/unusual circumstances, and all expected/common changes should have their dedicated form.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Member
        fields = ('email',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'rfid',
                  'group',
                  'picture')

